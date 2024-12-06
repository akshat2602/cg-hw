import copy
from OpenGL.GL import *
import glm

from .parametric import Parametric
from util import Shader


class Superquadric(Parametric):
    def __init__(
        self,
        shader: Shader,
        e1: float,  # North-south exponent
        e2: float,  # East-west exponent
        color: glm.vec3,
        model: glm.mat4 = glm.mat4(1.0),
    ):
        super().__init__(shader, 3, color, model)  # 3 indicates superquadric type
        self.e1 = e1
        self.e2 = e2

    def update_parameters(self, e1: float, e2: float):
        """Update superquadric parameters dynamically"""
        self.e1 = e1
        self.e2 = e2
        self.shader.use()
        self.shader.setFloat("e1", self.e1)
        self.shader.setFloat("e2", self.e2)

    def render(self, timeElapsedSinceLastFrame: float) -> None:
        self.shader.use()
        self.shader.setFloat("e1", self.e1)
        self.shader.setFloat("e2", self.e2)
        super().render(timeElapsedSinceLastFrame)
