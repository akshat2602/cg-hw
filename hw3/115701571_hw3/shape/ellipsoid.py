from OpenGL.GL import *
import glm
from collections import defaultdict

from util import Shader
from .icosahedron import Icosahedron


class Ellipsoid(Icosahedron):
    color: glm.vec3 = glm.vec3(0.4, 0.8, 0.3)

    def __init__(
        self,
        shader: Shader,
        vertexFile: str,
        scale: glm.vec3,
        model: glm.mat4 = glm.mat4(1.0),
        use_smooth_normals: bool = True,
    ):
        self.scale = scale
        super().__init__(shader, vertexFile, model, use_smooth_normals)

    def create_mesh(self, float_list):
        vertices = []
        vertex_to_index = {}
        vertex_to_normals = defaultdict(list)

        triangles = []
        for i in range(0, len(float_list), 9):
            v1 = glm.vec3(
                float_list[i] * self.scale.x,
                float_list[i + 1] * self.scale.y,
                float_list[i + 2] * self.scale.z,
            )
            v2 = glm.vec3(
                float_list[i + 3] * self.scale.x,
                float_list[i + 4] * self.scale.y,
                float_list[i + 5] * self.scale.z,
            )
            v3 = glm.vec3(
                float_list[i + 6] * self.scale.x,
                float_list[i + 7] * self.scale.y,
                float_list[i + 8] * self.scale.z,
            )

            edge1 = v2 - v1
            edge2 = v3 - v1
            faceNormal = glm.normalize(glm.cross(edge1, edge2))

            v1_key = (v1.x, v1.y, v1.z)
            v2_key = (v2.x, v2.y, v2.z)
            v3_key = (v3.x, v3.y, v3.z)

            for v_key in (v1_key, v2_key, v3_key):
                if v_key not in vertex_to_index:
                    vertex_to_index[v_key] = len(vertices)
                    vertices.append(glm.vec3(*v_key))

            vertex_to_normals[v1_key].append(faceNormal)
            vertex_to_normals[v2_key].append(faceNormal)
            vertex_to_normals[v3_key].append(faceNormal)

            triangles.append((v1, v2, v3, faceNormal))

        vertex_normals = {}
        for vertex_key, face_normals in vertex_to_normals.items():
            avg_normal = glm.vec3(0.0)
            for n in face_normals:
                avg_normal += n
            vertex_normals[vertex_key] = glm.normalize(avg_normal)

        vertexList = []
        for v1, v2, v3, faceNormal in triangles:
            for v in (v1, v2, v3):
                v_key = (v.x, v.y, v.z)
                normal = (
                    vertex_normals[v_key] if self.use_smooth_normals else faceNormal
                )
                vertexList.extend([v.x, v.y, v.z])
                vertexList.extend([normal.x, normal.y, normal.z])
                vertexList.extend([self.color.x, self.color.y, self.color.z])

        return glm.array(glm.float32, *vertexList)

    def subdivide(self):
        super().subdivide()
