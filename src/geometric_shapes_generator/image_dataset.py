# SPDX-License-Identifier: MIT

"""Optional PyTorch dataset; importing this module never instantiates datasets."""
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms import v2
from torchvision.transforms.functional import pil_to_tensor


class ImageCollection(Dataset):
    """Recursively load PNGs as RGB tensors; the dummy label is always zero.

    With no transform, values are float32 in [0, 1], shaped (3, H, W).
    Slices return a stacked batch, so transformed image sizes must match.
    """
    def __init__(self, path, transform=None):
        self.data = sorted(Path(path).rglob("*.png"))
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def _read(self, path):
        with Image.open(path) as image:
            tensor = pil_to_tensor(image.convert("RGB")).float() / 255
        return self.transform(tensor) if self.transform is not None else tensor

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            paths = self.data[idx]
            if not paths:
                raise IndexError("Cannot stack an empty image selection")
            return torch.stack([self._read(path) for path in paths]), [0] * len(paths)
        return self._read(self.data[idx]), 0


def grayscale_transform(size=300):
    """Crop to size x size, convert to grayscale, and normalize to [-1, 1]."""
    return v2.Compose([v2.Grayscale(), v2.CenterCrop((size, size)), v2.Normalize((0.5,), (0.5,))])
