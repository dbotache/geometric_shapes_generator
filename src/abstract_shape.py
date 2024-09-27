import os
from abc import ABC, abstractmethod
import uuid
import numpy as np

COLOR_LIST = [[0, 254, 0],      # green
              [132, 194, 234],  # blue
              [254, 0, 0],      # red
              # [255, 255, 255] # white
              ]


class AbstractShape(ABC):
    def __init__(self, destination, dim_x, dim_y, shape_size, alpha=1, color_list=None, shift=.8):
        self.destination = destination
        self.radius = None
        self.x = None
        self.y = None
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.shape_size = shape_size
        self.alpha = alpha
        self.color_list = color_list
        self.random_color = None
        self.rotation = None
        self.shift = shift

    def set_random_params(self, ax):
        """ Set all the common random parameters of a shape """
        if self.color_list is not None:
            colors_normalized = np.array(self.color_list) / 255.0
            self.random_color = colors_normalized[np.random.randint(0, len(colors_normalized))]
        else:
            self.random_color = np.random.rand(3, )

        ax.set_facecolor(self.random_color)
        self.radius = np.random.randint(round(self.shape_size * 0.5), self.shape_size)
        self.x = np.random.randint(-self.dim_x + self.radius * self.shift, self.dim_x - self.radius * self.shift)
        self.y = np.random.randint(-self.dim_y + self.radius * self.shift, self.dim_y - self.radius * self.shift)

        self.rotation = np.deg2rad(np.random.randint(-180, 180))

    def save_drawing(self, fig):
        """ Save the generated figure as a PNG """
        filepath = os.path.join(self.destination, f'{self.__class__.__name__}_{uuid.uuid4()}.png')
        fig.savefig(filepath)

    @abstractmethod
    def generate(self, ax):
        pass

    @abstractmethod
    def get_shape_coordinates(self):
        pass
