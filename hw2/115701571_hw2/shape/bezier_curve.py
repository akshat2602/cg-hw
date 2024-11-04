import copy
from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader


class BezierCurve(GLShape, Renderable):
    def __init__(self, shader: Shader, control_points: list[glm.vec2]):
        super().__init__(shader)
        self.control_points = []
        self.update_points(control_points)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * glm.sizeof(glm.float32), None
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update_points(self, control_points: list[glm.vec2]):
        self.control_points = copy.deepcopy(control_points)
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

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glPatchParameteri(GL_PATCH_VERTICES, 4)
        glDrawArrays(GL_PATCHES, 0, len(self.control_points))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
