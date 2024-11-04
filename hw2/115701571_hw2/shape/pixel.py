import copy
from OpenGL.GL import *
import glm
from .glshape import GLShape
from .renderable import Renderable
from util import Shader


class PixelData:
    def __init__(self, position: glm.vec2, color: glm.vec3):
        self.position = position
        self.color = color


class Pixel(GLShape, Renderable):
    def __init__(self, shader: Shader):
        super().__init__(shader)
        self.pixels = []
        self.pixel_size = 7.5

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 5 * glm.sizeof(glm.float32), None
        )

        # Color attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            5 * glm.sizeof(glm.float32),
            ctypes.c_void_p(2 * glm.sizeof(glm.float32)),
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update_pixels(self, pixels):
        self.pixels = copy.deepcopy(pixels)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        data = glm.array(
            glm.float32,
            *[
                value
                for pixel in self.pixels
                for value in (
                    pixel.position.x,
                    pixel.position.y,
                    pixel.color.r,
                    pixel.color.g,
                    pixel.color.b,
                )
            ]
        )
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data.ptr, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        if not self.pixels:
            return

        self.shader.use()
        self.shader.setMat3("model", self.model)
        self.shader.setFloat("pixelSize", self.pixel_size)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, len(self.pixels))
        glBindVertexArray(0)
