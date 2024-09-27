from abc import ABC
from src.abstract_shape import AbstractShape
import numpy as np
import matplotlib.pyplot as plt


class AbstractPolygonShape(AbstractShape, ABC):
    number_of_vertices = None

    def get_shape_coordinates(self):
        """ Get the coordinates of the polygon vertices """
        if not self.number_of_vertices:
            raise NotImplementedError("The number of vertices must be specified.")

        theta = np.linspace(0, 2 * np.pi, self.number_of_vertices, endpoint=False)
        points = np.stack((self.radius * np.cos(theta), self.radius * np.sin(theta)), axis=-1)
        points += np.array([self.x, self.y])
        return points

    def generate(self, ax):
        """ Generate the shape on the provided ax (matplotlib axis) """
        self.set_random_params(ax)
        coordinates = self.get_shape_coordinates()
        polygon = plt.Polygon(coordinates, closed=True, color=self.random_color, alpha=self.alpha)
        ax.add_patch(polygon)


class Triangle(AbstractPolygonShape):
    number_of_vertices = 3


class Square(AbstractPolygonShape):
    number_of_vertices = 4


class Pentagon(AbstractPolygonShape):
    number_of_vertices = 5


class Hexagon(AbstractPolygonShape):
    number_of_vertices = 6


class Heptagon(AbstractPolygonShape):
    number_of_vertices = 7


class Octagon(AbstractPolygonShape):
    number_of_vertices = 8


class Nonagon(AbstractPolygonShape):
    number_of_vertices = 9


class Circle(AbstractShape):
    def generate(self, ax):
        """ Generate a circle shape """
        self.set_random_params(ax)
        circle = plt.Circle((self.x, self.y), self.radius, color=self.random_color, alpha=self.alpha)
        ax.add_patch(circle)

    def get_shape_coordinates(self):
        pass


class Star(AbstractPolygonShape):
    def get_shape_coordinates(self):
        """ Generate star coordinates based on a 5-point star """
        points = []
        for i in range(10):
            angle = np.pi / 5 * i
            radius = self.radius if i % 2 == 0 else self.radius / 2
            x = self.x + radius * np.cos(angle)
            y = self.y + radius * np.sin(angle)
            points.append([x, y])
        return points
