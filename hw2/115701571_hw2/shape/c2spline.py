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

    def add_interpolation_point(self, point: glm.vec2, last_point: bool = False):
        if len(self.interpolation_points) < 3 or last_point:
            self.interpolation_points.append(point)
            self.control_points = copy.deepcopy(self.interpolation_points)
        else:
            self.interpolation_points.append(point)
            self._update_control_points()

        self._update_segments()
        self.interpolation_points = copy.deepcopy(self.control_points)
        return self.control_points

    def _update_control_points(self):
        self.control_points.append(self.interpolation_points[-1])
        last_3_points = self.interpolation_points[-3:]
        self.control_points.extend(self._add_derived_control_points(last_3_points))

    def _add_derived_control_points(
        self, last_3_points: list[glm.vec2]
    ) -> list[glm.vec2]:
        # Calculate the last 3 control points
        p0, p1, p2 = last_3_points
        p3 = glm.vec2(x=(2 * p2.x) - p1.x, y=(2 * p2.y) - p1.y)
        p4 = glm.vec2(x=p0.x + 2 * (p3.x - p2.x), y=p0.y + 2 * (p3.y - p2.y))
        return [p3, p4]

    def _update_segments(self):
        if len(self.control_points) < 4:
            return

        self.segments = []
        i = 0
        while i < len(self.control_points):
            segment = BezierCurve(self.shader, self.control_points[i : i + 4])
            self.segments.append(segment)
            i += 3

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        # Render individual segments
        for segment in self.segments:
            segment.render(timeElapsedSinceLastFrame, animate)
