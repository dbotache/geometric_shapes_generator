# SPDX-License-Identifier: MIT

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

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
                        dict(shapes=["NotAShape"])):
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


if __name__ == "__main__":
    unittest.main()
