from OpenGL.GL import *
import glm
import copy
import ctypes
from .glshape import GLShape
from .renderable import Renderable
from util import Shader


class CatmullRomSpline(GLShape, Renderable):
    def __init__(self, shader: Shader, control_points: list[glm.vec2] = []):
        super().__init__(shader)
        self.control_points = copy.deepcopy(control_points)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

    def add_control_point(self, point: glm.vec2):
        """Adds a control point and updates the spline."""
        self.control_points.append(point)
        self.update_vbo()

    def update_points(self, points: list[glm.vec2]):
        """Updates the control points and the VBO."""
        self.control_points = copy.deepcopy(points)
        self.update_vbo()

    def update_vbo(self):
        """Update the VBO with control points data."""
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        data = glm.array(
            glm.float32,
            *[coord for point in self.control_points for coord in (point.x, point.y)]
        )
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data.ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        """Render the Catmull-Rom spline by iterating through control points."""
        if len(self.control_points) < 4:
            return

        self.shader.use()
        self.shader.setMat3("model", self.model)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glPatchParameteri(GL_PATCH_VERTICES, 4)  # Ensure patches of 4 vertices

        # Render each segment with overlapping points
        for i in range(len(self.control_points) - 3):
            segment_data = glm.array(
                glm.float32,
                *[
                    coord
                    for point in self.control_points[i : i + 4]
                    for coord in (point.x, point.y)
                ]
            )
            glBufferData(
                GL_ARRAY_BUFFER, segment_data.nbytes, segment_data.ptr, GL_DYNAMIC_DRAW
            )

            glDrawArrays(GL_PATCHES, 0, 4)

        glDisableVertexAttribArray(0)
        glBindVertexArray(0)
