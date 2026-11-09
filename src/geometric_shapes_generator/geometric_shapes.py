# SPDX-License-Identifier: MIT

"""Render synthetic multi-shape scenes without a graphical display."""
import json
from pathlib import Path
from uuid import uuid4

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image

from .abstract_polygon_shape import (
    Circle, Heptagon, Hexagon, Nonagon, Octagon, Pentagon, Square, Star, Triangle,
)

SHAPE_TYPES = {cls.__name__: cls for cls in (
    Triangle, Circle, Heptagon, Octagon, Hexagon, Square, Star, Nonagon, Pentagon,
)}
DEFAULT_SHAPES = ("Triangle", "Circle", "Hexagon", "Square", "Nonagon", "Pentagon")


class GeometricShapes:
    def __init__(self, destination, size, dim_x, dim_y, shape_size, alpha=1,
                 color_list=None, bg_image="", shapes=None, seed=None):
        for name, value in (("size", size), ("dim_x", dim_x), ("dim_y", dim_y)):
            if not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(shape_size, int) or not 2 <= shape_size <= min(dim_x, dim_y):
            raise ValueError("shape_size must be an integer between 2 and min(dim_x, dim_y)")
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
        if seed is not None and (not isinstance(seed, (int, np.integer)) or seed < 0):
            raise ValueError("seed must be a nonnegative integer or None")
        if color_list is not None:
            colors = np.asarray(color_list, dtype=float)
            if (colors.ndim != 2 or colors.shape[1] != 3 or len(colors) == 0
                    or not np.all(np.isfinite(colors)) or np.any((colors < 0) | (colors > 255))):
                raise ValueError("color_list must contain RGB triples between 0 and 255")
            color_list = colors.tolist()
        names = tuple(DEFAULT_SHAPES if shapes is None else shapes)
        if not names or any(name not in SHAPE_TYPES for name in names):
            raise ValueError(f"shapes must be selected from: {', '.join(SHAPE_TYPES)}")
        self.destination = Path(destination)
        self.size, self.dim_x, self.dim_y = size, dim_x, dim_y
        self.shape_size, self.alpha, self.color_list = shape_size, float(alpha), color_list
        self.bg_image = bg_image
        self.seed = None if seed is None else int(seed)
        self.shape_names = names
        self.rng = np.random.default_rng(self.seed)
        self.shapes = [SHAPE_TYPES[name](
            self.destination, dim_x, dim_y, shape_size, alpha=self.alpha,
            color_list=color_list, rng=self.rng,
        ) for name in names]

    def generate(self, progress=None):
        """Write PNGs and a run JSON, returning image paths.

        An optional progress callback receives (completed_images, total_images).
        """
        background = None
        if self.bg_image:
            with Image.open(self.bg_image) as image:
                background = np.asarray(image.convert("RGB"))
        self.destination.mkdir(parents=True, exist_ok=True)
        metadata = {
            "schema_version": 1,
            "destination": str(self.destination.resolve()),
            "size": self.size,
            "dim_x": self.dim_x,
            "dim_y": self.dim_y,
            "shape_size": self.shape_size,
            "alpha": self.alpha,
            "color_list": self.color_list,
            "shapes": self.shape_names,
            "seed": self.seed,
            "bg_image": str(Path(self.bg_image).resolve()) if self.bg_image else None,
            "rng_state": self.rng.bit_generator.state,
        }
        paths = []
        for index in range(self.size):
            fig = Figure(figsize=(self.dim_x / 100, self.dim_y / 100), dpi=100)
            FigureCanvasAgg(fig)
            try:
                ax = fig.add_axes((0, 0, 1, 1))
                if background is not None:
                    ax.imshow(background, extent=(-self.dim_x, self.dim_x, -self.dim_y, self.dim_y))
                ax.set(xlim=(-self.dim_x, self.dim_x), ylim=(-self.dim_y, self.dim_y), aspect="equal")
                ax.axis("off")
                for shape in self.shapes:
                    shape.generate(ax)
                path = self.destination / f"scene_{uuid4().hex}.png"
                fig.savefig(path, dpi=100)
                paths.append(path)
            finally:
                fig.clear()
            if progress is not None:
                progress(index + 1, self.size)
        metadata["images"] = [path.name for path in paths]
        metadata_path = self.destination / f"run_{uuid4().hex}.json"
        with metadata_path.open("x", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2, allow_nan=False)
            file.write("\n")
        return paths
