from collections import defaultdict

from OpenGL.GL import *
import glm

from .mesh import Mesh
from util import Shader


class Tetrahedron(Mesh):

    def __init__(
        self,
        shader: Shader,
        vertexFile: str,
        model: glm.mat4 = glm.mat4(1.0),
        use_smooth_normals: bool = True,
        color: glm.vec3 = glm.vec3(0.31, 0.5, 1.0),
    ):

        # First, read all vertices and store unique ones
        self.color: glm.vec3 = color
        vertices = []
        vertex_to_index = {}
        vertex_to_normals = defaultdict(list)  # Store all face normals for each vertex

        with open(vertexFile, "r") as fin:
            floatList = list(map(float, fin.read().split()))

        assert len(floatList) % 9 == 0

        # Process each triangle
        triangles = []
        for i in range(0, len(floatList), 9):
            v1 = glm.vec3(floatList[i], floatList[i + 1], floatList[i + 2])
            v2 = glm.vec3(floatList[i + 3], floatList[i + 4], floatList[i + 5])
            v3 = glm.vec3(floatList[i + 6], floatList[i + 7], floatList[i + 8])

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
            # For each vertex in triangle
            for v in (v1, v2, v3):
                v_key = (v.x, v.y, v.z)
                # Use either smooth or flat normals based on parameter
                normal = vertex_normals[v_key] if use_smooth_normals else faceNormal

                # position xyz
                vertexList.extend([v.x, v.y, v.z])
                # normal xyz
                vertexList.extend([normal.x, normal.y, normal.z])
                # color rgb
                vertexList.extend([self.color.x, self.color.y, self.color.z])

        self.vertices: glm.array = glm.array(glm.float32, *vertexList)
        super().__init__(shader, self.vertices, model)
