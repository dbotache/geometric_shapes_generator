import os
from src.abstract_polygon_shape import *
import matplotlib.pyplot as plt

__ALL_GENERATORS__ = [
        'Triangle',
        'Circle',
        'Heptagon',
        'Octagon',
        'Hexagon',
        'Square',
        'Star',
        'Nonagon',
        'Pentagon'
    ]


class GeometricShapes:
    __GENERATORS__ = [
        'Triangle',
        'Circle',
        'Heptagon',
        'Octagon',
        'Hexagon',
        'Square',
        'Star',
        'Nonagon',
        'Pentagon'
    ]

    def __init__(self, destination, size, dim_x, dim_y, shape_size, alpha=1, color_list=None):
        self.size = size
        self.destination = destination
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.shape_size = shape_size
        self.alpha = alpha
        self.color_list = color_list

        if not os.path.exists(destination):
            os.makedirs(destination)

        # Create shape objects
        self.shapes = [
            globals()[shape](self.destination, self.dim_x, self.dim_y, self.shape_size, color_list=self.color_list) for
            shape in self.__GENERATORS__
        ]

    def generate(self):
        for _ in range(self.size):
            fig, ax = plt.subplots(figsize=(self.dim_x / 100, self.dim_y / 100))
            ax.set_xlim(-self.dim_x, self.dim_x)
            ax.set_ylim(-self.dim_y, self.dim_y)
            ax.set_aspect('equal')
            ax.axis('off')

            for shape in self.shapes:
                shape.generate(ax)

            shape.save_drawing(fig)

            plt.show()
            plt.close(fig)