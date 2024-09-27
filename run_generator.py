import argparse

from src.geometric_shapes import GeometricShapes


COLOR_LIST = [[0, 254, 0],      # green
              [132, 194, 234],  # blue
              [254, 0, 0],      # red
              # [255, 255, 255] # white
              ]


def main(args):

    if args.use_color_list:
        color_list = COLOR_LIST
    else:
        color_list = None

    destination = args.output_path
    datasize = args.datasize
    dim_x = args.resolution_x
    dim_y = args.resolution_y
    shape_size = args.shape_size
    color_list = COLOR_LIST

    generator = GeometricShapes(destination=destination,
                                size=datasize,
                                dim_x=dim_x,
                                dim_y=dim_y,
                                shape_size=shape_size,
                                color_list=color_list)
    generator.generate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_path',metavar='output_path', type=str, default='./output', help='Output directory for generated files')
    parser.add_argument('--datasize',metavar='datasize', type=int, default=10, help='Number of samples')
    parser.add_argument('--resolution_x',metavar='resolution_x', type=int, default=1800, help='resolution in x-axis')
    parser.add_argument('--resolution_y',metavar='resolution_y', type=int, default=1350, help='resolution in y-axis')
    parser.add_argument('--shape_size',metavar='shape_size', type=int, default=500, help='Size of gemoetric shapes')
    parser.add_argument('--use_color_list',metavar='use_color_list', type=bool, default=1, help='Flag for using predefined COLOR_LIST')
    args = parser.parse_args()

    main(args)