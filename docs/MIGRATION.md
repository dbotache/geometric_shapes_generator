# Structure and behavior changes

| Previous location or API | Current location or API |
| --- | --- |
| `src/geometric_shapes.py` | `src/geometric_shapes_generator/geometric_shapes.py` |
| `from src.geometric_shapes import GeometricShapes` | `from geometric_shapes_generator import GeometricShapes` |
| `src/abstract_shape.py`, `src/abstract_polygon_shape.py` | Same module names inside `geometric_shapes_generator` |
| `src/image_dataset.py` | `geometric_shapes_generator.image_dataset` (optional dependencies) |
| `background*.png` | `assets/background*.png` |
| `Generator.ipynb` | `notebooks/Generator.ipynb` |
| Editing `__GENERATORS__` | Pass `shapes=[...]`; register new classes in `SHAPE_TYPES` |
| Module-level `ds_low`, `ds_full` | Explicitly instantiate `ImageCollection(path, transform=...)` |

Install with `python -m pip install -e .` before using the root launcher or notebooks. Underscore CLI flags remain accepted. Old imports require updating; no `sys.path` modification is needed.

The CLI now respects disabled palette selection and the supplied background path. Opacity reaches every shape, rotations are applied, and output names describe multi-shape scenes. Rendering fills the requested pixel dimensions, without the former figure margins. These bug fixes change generated pixels compared with the original implementation. A seed controls the new generator; it does not reproduce historical outputs.

Dataset loading no longer creates example datasets during import. Single-item and slice reads both return RGB float32 data in [0, 1] before transforms, rather than unnormalized [0, 255] values. Remove any extra division by 255 in downstream code. The optional grayscale helper maps [0, 1] to [-1, 1].
