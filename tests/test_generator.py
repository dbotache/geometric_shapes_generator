# SPDX-License-Identifier: MIT

import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from geometric_shapes_generator import GeometricShapes
from geometric_shapes_generator.cli import main
from geometric_shapes_generator.geometric_shapes import SHAPE_TYPES


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def generator(self, **options):
        defaults = dict(destination=self.root / "images", size=2, dim_x=320,
                        dim_y=240, shape_size=70, seed=5)
        defaults.update(options)
        return GeometricShapes(**defaults)

    def test_count_dimensions_and_all_shape_types(self):
        paths = self.generator(shapes=list(SHAPE_TYPES)).generate()
        self.assertEqual(len(paths), 2)
        self.assertNotEqual(paths[0], paths[1])
        for path in paths:
            self.assertTrue(path.name.startswith("scene_"))
            with Image.open(path) as image:
                self.assertEqual(image.size, (320, 240))
                self.assertGreater(len(np.unique(np.asarray(image).reshape(-1, 4), axis=0)), 2)

    def test_custom_background_and_zero_opacity(self):
        background = self.root / "custom.png"
        Image.new("RGB", (12, 8), (17, 61, 203)).save(background)
        path = self.generator(size=1, bg_image=background, alpha=0).generate()[0]
        with Image.open(path) as image:
            rgb = np.asarray(image.convert("RGB"))
            self.assertTrue(np.all(rgb == (17, 61, 203)))

    def test_seed_reproduces_pixels_but_not_filenames(self):
        first = self.generator(size=1).generate()[0]
        second = self.generator(size=1).generate()[0]
        self.assertNotEqual(first.name, second.name)
        with Image.open(first) as a, Image.open(second) as b:
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b))

    def test_background_failure_does_not_create_output(self):
        generator = self.generator(bg_image=self.root / "missing.png")
        with self.assertRaises(FileNotFoundError):
            generator.generate()
        self.assertFalse(generator.destination.exists())

    def test_invalid_configuration(self):
        for options in (dict(size=0), dict(dim_x=-1), dict(shape_size=1),
                        dict(shape_size=241), dict(alpha=2), dict(color_list=[]),
                        dict(color_list=[[0, 1]]), dict(color_list=[[256, 0, 0]]),
                        dict(color_list=[[float("nan"), 0, 0]]), dict(shapes=[]),
                        dict(shapes=["NotAShape"]), dict(seed=-1), dict(seed=1.5)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.generator(**options)

    def test_cli_legacy_false_and_random_colors_agree(self):
        common = ["--datasize", "1", "--resolution_x", "320", "--resolution_y", "240",
                  "--shape_size", "70", "--seed", "18", "--shapes", "Circle"]
        images = []
        for name, flags in (("legacy", ["--use_color_list", "false"]),
                            ("random", ["--random-colors"]), ("palette", [])):
            output = self.root / name
            with contextlib.redirect_stdout(io.StringIO()):
                main(common + ["--output_path", str(output)] + flags)
            with Image.open(next(output.glob("*.png"))) as image:
                images.append(np.array(image))
        np.testing.assert_array_equal(images[0], images[1])
        self.assertFalse(np.array_equal(images[0], images[2]))

    def test_run_settings_include_actual_configuration_and_images(self):
        background = self.root / "background.png"
        Image.new("RGB", (10, 10), (10, 20, 30)).save(background)
        generator = self.generator(
            bg_image=background, alpha=np.float32(0.5), color_list=np.array([[20, 80, 160]]),
            seed=np.int64(12), shapes=["Circle", "Star"],
        )
        paths = generator.generate()
        metadata = json.loads(next(generator.destination.glob("run_*.json")).read_text())
        for key, expected in {
            "schema_version": 1, "size": 2, "dim_x": 320, "dim_y": 240,
            "shape_size": 70, "alpha": 0.5, "seed": 12,
            "color_list": [[20, 80, 160]], "shapes": ["Circle", "Star"],
            "bg_image": str(background.resolve()), "destination": str(generator.destination.resolve()),
            "images": [path.name for path in paths],
        }.items():
            with self.subTest(key=key):
                self.assertEqual(metadata[key], expected)
        self.assertEqual(metadata["rng_state"]["bit_generator"], "PCG64")

    def test_repeated_runs_keep_metadata_and_can_replay_unseeded_content(self):
        generator = self.generator(size=1, seed=None)
        first = generator.generate()[0]
        second = generator.generate()[0]
        manifests = [json.loads(path.read_text()) for path in generator.destination.glob("run_*.json")]
        self.assertEqual(len(manifests), 2)
        self.assertEqual({m["images"][0] for m in manifests}, {first.name, second.name})
        metadata = next(m for m in manifests if m["images"] == [second.name])
        self.assertIsNone(metadata["seed"])
        self.assertIsNone(metadata["bg_image"])
        self.assertIsNone(metadata["color_list"])
        replay = self.generator(size=1)
        replay.rng.bit_generator.state = metadata["rng_state"]
        replayed = replay.generate()[0]
        with Image.open(second) as a, Image.open(replayed) as b:
            np.testing.assert_array_equal(np.asarray(a), np.asarray(b))

    def test_progress_callback_runs_after_each_image_is_saved(self):
        events = []
        generator = self.generator(size=3)

        def progress(completed, total):
            events.append((completed, total))
            self.assertEqual(len(list(generator.destination.glob("*.png"))), completed)

        generator.generate(progress=progress)
        self.assertEqual(events, [(1, 3), (2, 3), (3, 3)])

    def test_failed_render_does_not_report_progress_or_complete_metadata(self):
        events = []
        generator = self.generator()
        with patch("matplotlib.figure.Figure.savefig", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(OSError, "disk full"):
                generator.generate(progress=lambda *event: events.append(event))
        self.assertEqual(events, [])
        self.assertEqual(list(generator.destination.glob("run_*.json")), [])

    def test_palette_is_snapshotted_and_renders_original_rgb_values(self):
        palette = [[20, 80, 160]]
        generator = self.generator(size=1, shapes=["Circle"], color_list=palette)
        palette[0][:] = [255, 0, 0]
        path = generator.generate()[0]
        with Image.open(path) as image:
            rgb = np.array(image.convert("RGB"))
        self.assertTrue(np.any(np.all(rgb == (20, 80, 160), axis=-1)))
        self.assertFalse(np.any(np.all(rgb == (255, 0, 0), axis=-1)))
        metadata = json.loads(next(generator.destination.glob("run_*.json")).read_text())
        self.assertEqual(metadata["color_list"], [[20, 80, 160]])

    def test_cli_progress_interval_and_disable(self):
        common = ["--datasize", "5", "--resolution-x", "160", "--resolution-y", "120",
                  "--shape-size", "30", "--seed", "1"]
        for interval, expected in ((2, ["Progress: 2/5 images", "Progress: 4/5 images", "Progress: 5/5 images"]),
                                   (0, [])):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main(common + ["--output-path", str(self.root / str(interval)), "--progress-every", str(interval)])
            self.assertEqual([line for line in output.getvalue().splitlines() if line.startswith("Progress:")], expected)
            self.assertIn("Generated 5 images", output.getvalue())

    def test_cli_invalid_progress_interval_creates_no_output(self):
        output = self.root / "invalid"
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main(["--progress-every", "-1", "--output-path", str(output)])
        self.assertEqual(error.exception.code, 2)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
