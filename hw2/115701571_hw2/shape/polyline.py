import copy
from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader


class Polyline(GLShape, Renderable):
    def __init__(self, shader: Shader):
        super().__init__(shader)
        self.points = []

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 2 * glm.sizeof(glm.float32), None
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update_points(self, points):
        self.points = copy.deepcopy(points)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        data = glm.array(
            glm.float32,
            *[coord for point in self.points for coord in (point.x, point.y)]
        )
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data.ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        if len(self.points) < 2:
            return

        self.shader.use()
        self.shader.setMat3("model", self.model)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINE_STRIP, 0, len(self.points))
        glBindVertexArray(0)
