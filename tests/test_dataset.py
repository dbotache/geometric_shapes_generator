# SPDX-License-Identifier: MIT

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

try:
    import torch
    from geometric_shapes_generator.image_dataset import ImageCollection, grayscale_transform
except ImportError:
    torch = None


@unittest.skipIf(torch is None, "Install .[dataset] for optional PyTorch checks")
class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "nested").mkdir()
        Image.new("RGBA", (32, 32), (255, 255, 255, 255)).save(self.root / "a.png")
        Image.new("L", (32, 32), 0).save(self.root / "nested/b.png")
        (self.root / "run_example.json").write_text('{"images": ["a.png", "nested/b.png"]}')

    def test_rgb_conversion_and_slice_consistency(self):
        dataset = ImageCollection(self.root)
        self.assertEqual(len(dataset), 2)  # Run metadata is not an image sample.
        image, label = dataset[0]
        batch, labels = dataset[:2]
        self.assertEqual(image.shape, (3, 32, 32))
        self.assertEqual(image.dtype, torch.float32)
        self.assertEqual(label, 0)
        self.assertEqual(labels, [0, 0])
        self.assertEqual(batch.shape, (2, 3, 32, 32))
        torch.testing.assert_close(batch[0], image)
        self.assertEqual(image.min().item(), 1)
        self.assertEqual(batch[1].max().item(), 0)

    def test_normalized_grayscale_and_empty_selection(self):
        dataset = ImageCollection(self.root, grayscale_transform(16))
        batch, _ = dataset[:]
        self.assertEqual(batch.shape, (2, 1, 16, 16))
        self.assertAlmostEqual(batch[0].mean().item(), 1, places=3)
        self.assertAlmostEqual(batch[1].mean().item(), -1, places=3)
        with self.assertRaises(IndexError):
            dataset[0:0]
        self.assertEqual(len(ImageCollection(self.root / "missing")), 0)


if __name__ == "__main__":
    unittest.main()
