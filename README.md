# Geometric Shapes Generator

Generate synthetic PNG scenes for computer vision experiments, image reconstruction, and prototyping. Each image contains one instance of every selected shape, with randomized size, position, rotation, and color. Shapes can overlap or be partly clipped; this is an **unlabeled image generator**, not an object-detection annotation tool.

## Install

Use Python 3.10 or newer. Python 3.12 is a practical starting point if you also need PyTorch.

```bash
git clone https://github.com/dbotache/geometric_shapes_generator.git
cd geometric_shapes_generator
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The base installation needs only NumPy, Matplotlib, and Pillow. Rendering works without a display server.

## Generate images

From the repository root:

```bash
generate-shapes --output-path output/demo --datasize 10 \
  --resolution-x 640 --resolution-y 480 --shape-size 150 --seed 42
```

Use a supplied background, a custom shape selection, and random colors:

```bash
generate-shapes --output-path output/background --datasize 20 \
  --resolution-x 300 --resolution-y 300 --shape-size 100 \
  --bg-image assets/background_low.png --random-colors \
  --shapes Circle Triangle Star --seed 7
```

`python -m geometric_shapes_generator` and `python run_generator.py` invoke the same CLI after installation. Run `generate-shapes --help` for all options. Paths are relative to your current directory; use absolute paths when launching elsewhere.

| Option | Default | Meaning |
| --- | --- | --- |
| `--output-path` | `output` | Created automatically; existing images are retained |
| `--datasize` | `10` | Number of PNG scenes to add |
| `--resolution-x`, `--resolution-y` | `1800`, `1350` | Exact output width and height in pixels |
| `--shape-size` | `500` | Exclusive upper bound on shape radius in scene coordinates |
| `--bg-image` | empty | Image to stretch over the canvas; otherwise white |
| `--random-colors` | off | Random RGB colors instead of the red/green CLI palette |
| `--alpha` | `1` | Shape opacity between zero and one |
| `--shapes` | Triangle Circle Hexagon Square Nonagon Pentagon | One instance of each listed shape per scene |
| `--seed` | unset | Reproduce scene content within the same dependency environment |
| `--progress-every` | `100` | Print progress every N images and at completion; `0` disables it |

Supported shapes: Triangle, Circle, Square, Pentagon, Hexagon, Heptagon, Octagon, Nonagon, and Star. Legacy underscore option names such as `--output_path` and `--bg_image` remain accepted. `--use_color_list false` also selects random colors.

The scene spans `[-width, width]` and `[-height, height]`; a radius of 100 scene units occupies about 50 pixels at the output scale. Radii are sampled from approximately half `shape_size` up to, but excluding, `shape_size`. Set `2 <= shape_size <= min(width, height)`; reduce the default when generating small images. Rotation changes orientation; a square may appear as a diamond.

Outputs are named `scene_<uuid>.png`. A seed fixes image content, not filenames. Each file contains the entire scene, and filenames do not identify a single shape class. There are no class labels, masks, or bounding boxes.

Each successful run also saves `run_<uuid>.json` beside the images. It records the seed, selected shapes, palette, dimensions, opacity, background path, starting RNG state, and the image filenames for that run. Repeated runs retain earlier images and metadata. Paths refer to your local files; metadata does not embed a copy of the background or your dependency environment.

## Use and adapt the Python API

```python
from geometric_shapes_generator import GeometricShapes

paths = GeometricShapes(
    destination="output/custom",
    size=25,
    dim_x=640,
    dim_y=480,
    shape_size=150,
    color_list=[[255, 140, 0], [40, 100, 220]],  # RGB values in [0, 255]
    alpha=0.8,
    shapes=["Circle", "Pentagon"],
    seed=123,
).generate()
print(paths[0])
```

With `color_list=None`, the API uses random RGB colors. To add a polygon, subclass `AbstractPolygonShape`, set `number_of_vertices`, and register it in `SHAPE_TYPES` in `geometric_shapes.py`. For another geometry, implement `AbstractShape.generate()` and `get_shape_coordinates()`. Add annotation export in the generation loop if your task needs supervised labels; the existing PyTorch loader returns a placeholder zero label.

The palette is copied and normalized when the generator is constructed; changing your original palette list afterward does not change a run. The API is silent by default. Use `.generate(progress=lambda completed, total: print(f"{completed}/{total}"))` to receive an update after each image is saved.

For content replay, construct a generator with the recorded settings and the same dependency environment. Restoring `generator.rng.bit_generator.state = settings["rng_state"]` before `.generate()` also reproduces unseeded runs and later runs from a reused generator. A seed alone reproduces the first run of a fresh generator. The background file must have the same contents.

## Optional PyTorch loader

```bash
python -m pip install -e '.[dataset]'
```

```python
from torch.utils.data import DataLoader
from geometric_shapes_generator.image_dataset import ImageCollection, grayscale_transform

dataset = ImageCollection("output/demo", transform=grayscale_transform(size=300))
images, placeholder_labels = next(iter(DataLoader(dataset, batch_size=4)))
# images: [batch, 1, 300, 300], float32, normalized to [-1, 1]
```

Without a transform, images are RGB tensors of shape `[3, H, W]` with float32 values in `[0, 1]`. The loader recursively finds PNGs in sorted path order and handles integer indices and slices consistently. Crop or resize mixed-size inputs before batching. An empty folder gives a dataset of length zero; an empty slice cannot be stacked. Install a matching Torch/Torchvision pair for your CPU or GPU using the [official PyTorch installer](https://pytorch.org/get-started/locally/) if the default packages do not fit your system.

## Optional notebook

```bash
python -m pip install -e '.[notebook]'
jupyter lab notebooks/Generator.ipynb
```

The notebook uses the installed package. Its destination is relative to the notebook kernel's working directory.

## Repository layout

```text
src/geometric_shapes_generator/  Installable package, CLI, shapes, optional dataset
assets/                         Example background images
notebooks/Generator.ipynb        Interactive widget example
run_generator.py                Compatibility CLI launcher
pyproject.toml                  Dependencies and executable entry point
tests/                          Regression tests using Python unittest
docs/                           Migration and licensing scope
```

The former `src.*` imports have moved to `geometric_shapes_generator.*`; see [migration notes](docs/MIGRATION.md). Backgrounds and the notebook are repository examples and are not included in the Python wheel.

## Development and checks

```bash
python -m unittest discover -s tests -v
python -m pip install build
python -m build
```

The dataset-specific checks skip when Torch/Torchvision are not installed. To run them, install `.[dataset]` first. Dependencies in `pyproject.toml` are minimum supported targets rather than a lockfile. Freeze your environment for an experiment if repeatability matters.

## License

Original source code, tests, notebook code, build/configuration files, and documentation are licensed under the [MIT License](LICENSE). Copyright notices for Diego Botache and Sebastian Schulze are retained in the license file.

The example background images in `assets/` are excluded from that grant because their provenance and redistribution rights are unverified. Dependencies retain their own licenses. See [licensing scope and attribution](docs/LICENSING.md) before redistributing those assets or generated images containing them.
