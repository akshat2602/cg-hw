import glm
from OpenGL.GL import *
from util import Shader


class Parametric:
    def __init__(
        self,
        shader: Shader,
        shape_type: int,  # 0=sphere, 1=cylinder, 2=cone, 3=torus
        color: glm.vec3,
        model: glm.mat4 = glm.mat4(1.0),
    ):
        self.shader = shader
        self.shape_type = shape_type
        self.color = color
        self.model = model
        self.dummy = glm.array(glm.float32, 0.0)
        self.subdivision_level = 15

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 1, GL_FLOAT, GL_FALSE, glm.sizeof(glm.float32), None)

        glBufferData(GL_ARRAY_BUFFER, self.dummy.nbytes, self.dummy.ptr, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render(self, timeElapsedSinceLastFrame: float) -> None:
        self.shader.use()
        self.shader.setMat4("model", self.model)
        self.shader.setVec3("objectColor", self.color)
        self.shader.setInt("shapeType", self.shape_type)

        glBindVertexArray(self.vao)
        glPatchParameteri(GL_PATCH_VERTICES, 1)
        glDrawArrays(GL_PATCHES, 0, 1)
        glBindVertexArray(0)
