# SPDX-License-Identifier: MIT

"""Shared parameters for drawable shapes."""
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

import numpy as np


class AbstractShape(ABC):
    def __init__(self, destination, dim_x, dim_y, shape_size, alpha=1,
                 color_list=None, shift=0.8, rng=None):
        self.destination = Path(destination)
        self.dim_x, self.dim_y = dim_x, dim_y
        self.shape_size, self.alpha = shape_size, alpha
        self.color_list, self.shift = color_list, shift
        self._palette = None if color_list is None else np.asarray(color_list, dtype=float) / 255
        self.rng = rng if rng is not None else np.random.default_rng()
        self.radius = self.x = self.y = self.random_color = self.rotation = None

    def set_random_params(self, ax):
        """Pick a color, radius, center, and rotation in scene coordinates."""
        if self._palette is not None:
            self.random_color = self._palette[self.rng.integers(len(self._palette))]
        else:
            self.random_color = self.rng.random(3)
        self.radius = self.rng.integers(max(1, round(self.shape_size * 0.5)), self.shape_size)
        self.x = self.rng.uniform(-self.dim_x + self.radius * self.shift,
                                  self.dim_x - self.radius * self.shift)
        self.y = self.rng.uniform(-self.dim_y + self.radius * self.shift,
                                  self.dim_y - self.radius * self.shift)
        self.rotation = self.rng.uniform(-np.pi, np.pi)

    def save_drawing(self, fig):
        filepath = self.destination / f"{type(self).__name__}_{uuid4().hex}.png"
        fig.savefig(filepath)
        return filepath

    @abstractmethod
    def generate(self, ax):
        pass

    @abstractmethod
    def get_shape_coordinates(self):
        pass
