# SPDX-License-Identifier: MIT

"""Command-line interface for generating image collections."""
import argparse

from .geometric_shapes import DEFAULT_SHAPES, SHAPE_TYPES, GeometricShapes

COLOR_LIST = [[0, 254, 0], [254, 0, 0]]


def parse_bool(value):
    if value.lower() in {"true", "1", "yes"}:
        return True
    if value.lower() in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true/false or 1/0")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate PNG scenes with random geometric shapes.")
    parser.add_argument("--output-path", "--output_path", default="output")
    parser.add_argument("--datasize", type=int, default=10, help="Number of images")
    parser.add_argument("--resolution-x", "--resolution_x", type=int, default=1800)
    parser.add_argument("--resolution-y", "--resolution_y", type=int, default=1350)
    parser.add_argument("--shape-size", "--shape_size", type=int, default=500,
                        help="Maximum radius in scene units; 2 through min(resolution)")
    parser.add_argument("--use-color-list", "--use_color_list", type=parse_bool,
                        nargs="?", const=True, default=True, help="Use the red/green palette (default: true)")
    parser.add_argument("--random-colors", dest="use_color_list", action="store_false")
    parser.add_argument("--bg-image", "--bg_image", default="", help="Background image path")
    parser.add_argument("--alpha", type=float, default=1)
    parser.add_argument("--shapes", nargs="+", choices=SHAPE_TYPES, default=DEFAULT_SHAPES)
    parser.add_argument("--seed", type=int, help="Reproduce scene content; filenames remain unique")
    parser.add_argument("--progress-every", type=int, default=100,
                        help="Report every N images and at completion; 0 disables progress")
    args = parser.parse_args(argv)
    if args.progress_every < 0:
        parser.error("--progress-every must be nonnegative")

    def report_progress(completed, total):
        if args.progress_every and (completed % args.progress_every == 0 or completed == total):
            print(f"Progress: {completed}/{total} images", flush=True)

    try:
        generator = GeometricShapes(
            destination=args.output_path, size=args.datasize, dim_x=args.resolution_x,
            dim_y=args.resolution_y, shape_size=args.shape_size, alpha=args.alpha,
            color_list=COLOR_LIST if args.use_color_list else None,
            bg_image=args.bg_image, shapes=args.shapes, seed=args.seed,
        )
        paths = generator.generate(progress=report_progress)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"Generated {len(paths)} images in {generator.destination.resolve()}")
