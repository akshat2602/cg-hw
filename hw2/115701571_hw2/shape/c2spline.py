from OpenGL.GL import *
import glm
import copy
from .glshape import GLShape
from .renderable import Renderable
from util import Shader
from .bezier_curve import BezierCurve


class C2Spline(GLShape, Renderable):
    def __init__(self, shader: Shader):
        super().__init__(shader)
        self.interpolation_points = []
        self.control_points = []
        self.segments = []

    def add_interpolation_point(self, point: glm.vec2):
        self.interpolation_points.append(point)
        self._update_control_points()
        self._update_segments()
        self._update_vbo()

    def _update_control_points(self):
        self.control_points = copy.deepcopy(self.interpolation_points)

    def _update_segments(self):
        self.segments = []
        i = 0
        while i < len(self.control_points):
            segment = BezierCurve(self.shader, self.control_points[i : i + 4])
            self.segments.append(segment)
            i += 3

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        # Render individual segments
        for segment in self.segments:
            print(segment.control_points)
            segment.render(timeElapsedSinceLastFrame, animate)

    def update_points(self, points: list[glm.vec2]):
        self.interpolation_points = copy.deepcopy(points)
        self._update_control_points()
        self._update_segments()
