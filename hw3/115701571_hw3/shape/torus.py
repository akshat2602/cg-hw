from OpenGL.GL import *
import glm

from .mesh import Mesh
from util import Shader


class Torus(Mesh):
    def __init__(
        self,
        shader: Shader,
        R: float,  # Major radius
        r: float,  # Minor radius
        color: glm.vec3,
        model: glm.mat4 = glm.mat4(1.0),
    ):

        self.R = R
        self.r = r
        self.color = color
        self.subdivision_level = 15

        # Generate initial mesh vertices
        vertices = self.create_mesh()
        super().__init__(shader, vertices, model)

    def create_mesh(self):
        vertices = []

        # Generate triangles for torus surface
        for i in range(self.subdivision_level):
            for j in range(self.subdivision_level):
                # Calculate vertices for current quad
                u0 = i / self.subdivision_level
                u1 = (i + 1) / self.subdivision_level
                v0 = j / self.subdivision_level
                v1 = (j + 1) / self.subdivision_level

                # Generate two triangles for the quad
                for u, v in [
                    (u0, v0),
                    (u1, v0),
                    (u0, v1),  # First triangle
                    (u1, v0),
                    (u1, v1),
                    (u0, v1),
                ]:  # Second triangle
                    # Handle wrapping around
                    u = u % 1.0
                    v = v % 1.0

                    phi = 2.0 * glm.pi() * u
                    theta = 2.0 * glm.pi() * v

                    # Position
                    x = (self.R + self.r * glm.cos(theta)) * glm.cos(phi)
                    y = self.r * glm.sin(theta)
                    z = (self.R + self.r * glm.cos(theta)) * glm.sin(phi)

                    # Normal
                    nx = glm.cos(theta) * glm.cos(phi)
                    ny = glm.sin(theta)
                    nz = glm.cos(theta) * glm.sin(phi)
                    norm = glm.normalize(glm.vec3(nx, ny, nz))

                    vertices.extend([x, y, z])  # Position
                    vertices.extend([norm.x, norm.y, norm.z])  # Normal
                    vertices.extend([self.color.x, self.color.y, self.color.z])  # Color

        return glm.array(glm.float32, *vertices)

    def subdivide(self):
        if self.subdivision_level == 15:
            self.subdivision_level = 30
        elif self.subdivision_level == 30:
            self.subdivision_level = 60

        # Regenerate mesh with new subdivision level
        self.vertices = self.create_mesh()
        super().__init__(self.shader, self.vertices, self.model)
