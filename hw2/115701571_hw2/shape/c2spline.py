from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader
from .bezier_curve import BezierCurve


class C2PieceWiseSpline(GLShape, Renderable):
    def __init__(self, shader: Shader):
        super().__init__(shader)
        self.interpolation_points = []
        self.control_points = []
        self.segments = []

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * glm.sizeof(glm.float32), None
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def add_interpolation_point(self, point: glm.vec2):
        self.interpolation_points.append(point)
        self._update_control_points()
        self._update_segments()
        self._update_vbo()

    def _update_control_points(self):
        self.control_points = []
        n = len(self.interpolation_points)
        if n < 2:
            return

        # Set the first control points for the first segment
        for i in range(n - 1):
            p0 = self.interpolation_points[i]
            p3 = self.interpolation_points[i + 1]

            # Calculate p1 and p2 based on neighbors for C2 continuity
            if i == 0:
                # For the first segment, we only have one neighbor
                p1 = p0 + (p3 - p0) / 3
                next_p = self.interpolation_points[i + 2] if i + 2 < n else p3
                p2 = p3 - (next_p - p0) / 6  # Adjust p2 based on next segment
            elif i == n - 2:
                # For the last segment, adjust p2 only
                prev_p = self.interpolation_points[i - 1]
                p1 = p0 + (p3 - prev_p) / 6
                p2 = p3 - (p3 - p0) / 3
            else:
                # For intermediate segments, ensure both p1 and p2 adjustments
                prev_p = self.interpolation_points[i - 1]
                next_p = self.interpolation_points[i + 2]

                # p1 is a third of the distance between prev_p and p3 for smooth transitions
                p1 = p0 + (p3 - prev_p) / 6
                # p2 is adjusted similarly for smooth curvature
                p2 = p3 - (next_p - p0) / 6

            # Add the computed control points for the current segment
            self.control_points.extend([p0, p1, p2, p3])

    def _update_segments(self):
        self.segments = []

        num_points = len(self.control_points)
        if num_points < 4:
            return

        for i in range(0, num_points - 3, 4):
            segment = BezierCurve(self.shader, self.control_points[i : i + 4])
            self.segments.append(segment)

    def _update_vbo(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        data = glm.array(
            glm.float32,
            *[coord for point in self.control_points for coord in (point.x, point.y)]
        )
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data.ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        self.shader.use()
        self.shader.setMat3("model", self.model)

        glPatchParameteri(GL_PATCH_VERTICES, 4)

        # Render each Bezier segment independently
        for segment in self.segments:
            segment.render(timeElapsedSinceLastFrame, animate)
            # print(segment.control_points)

    def update_points(self, points: list[glm.vec2]):
        self.interpolation_points = points
        self._update_control_points()
        self._update_segments()
        self._update_vbo()
