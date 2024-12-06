from collections import defaultdict
from OpenGL.GL import *
import glm

from .mesh import Mesh
from util import Shader


class Dodecahedron(Mesh):
    def __init__(
        self,
        shader: Shader,
        vertexFile: str,
        model: glm.mat4 = glm.mat4(1.0),
        use_smooth_normals: bool = True,
        color: glm.vec3 = glm.vec3(0.8, 0.2, 0.8),
    ):
        self.shader = shader
        self.use_smooth_normals = use_smooth_normals
        self.color = color
        self.subdivision_level = 0

        # Read vertices
        with open(vertexFile, "r") as fin:
            float_list = list(map(float, fin.read().split()))
            self.faces = []  # List of faces, each face is list of triangles

            # Group triangles into faces (12 pentagonal faces)
            for pentagon_idx in range(0, len(float_list), 27):
                face_triangles = []
                for i in range(0, 27, 9):
                    idx = pentagon_idx + i
                    v1 = glm.vec3(
                        float_list[idx], float_list[idx + 1], float_list[idx + 2]
                    )
                    v2 = glm.vec3(
                        float_list[idx + 3], float_list[idx + 4], float_list[idx + 5]
                    )
                    v3 = glm.vec3(
                        float_list[idx + 6], float_list[idx + 7], float_list[idx + 8]
                    )
                    face_triangles.append([v1, v2, v3])
                self.faces.append(face_triangles)

        vertices = self.create_mesh()
        super().__init__(shader, vertices, model)

    def create_mesh(self):
        vertex_data = []

        if self.use_smooth_normals:
            # Build vertex normal map for all vertices
            vertex_normals = {}

            # For a sphere, the normal at each point is just the normalized position
            for face in self.faces:
                for triangle in face:
                    for vertex in triangle:
                        key = (
                            round(vertex.x, 6),
                            round(vertex.y, 6),
                            round(vertex.z, 6),
                        )
                        if key not in vertex_normals:
                            vertex_normals[key] = glm.normalize(vertex)

            # Generate vertex data with smooth normals
            for face in self.faces:
                for triangle in face:
                    for vertex in triangle:
                        key = (
                            round(vertex.x, 6),
                            round(vertex.y, 6),
                            round(vertex.z, 6),
                        )
                        normal = vertex_normals[key]
                        vertex_data.extend(
                            [
                                vertex.x,
                                vertex.y,
                                vertex.z,
                                normal.x,
                                normal.y,
                                normal.z,
                                self.color.x,
                                self.color.y,
                                self.color.z,
                            ]
                        )
        else:
            # Generate vertex data with flat normals
            for face in self.faces:
                for triangle in face:
                    edge1 = triangle[1] - triangle[0]
                    edge2 = triangle[2] - triangle[0]
                    normal = glm.normalize(glm.cross(edge1, edge2))

                    for vertex in triangle:
                        vertex_data.extend(
                            [
                                vertex.x,
                                vertex.y,
                                vertex.z,
                                normal.x,
                                normal.y,
                                normal.z,
                                self.color.x,
                                self.color.y,
                                self.color.z,
                            ]
                        )

        return glm.array(glm.float32, *vertex_data)

    def subdivide(self):
        if self.subdivision_level >= 2:
            return

        self.subdivision_level += 1
        new_faces = []

        # Get radius from any vertex
        radius = glm.length(self.faces[0][0][0])

        # Process each pentagonal face separately
        for face in self.faces:
            new_face_triangles = []
            for triangle in face:
                # Calculate midpoints and project onto sphere
                midpoints = []
                for i in range(3):
                    v1 = triangle[i]
                    v2 = triangle[(i + 1) % 3]

                    # Calculate midpoint and project onto sphere
                    mid = (v1 + v2) * 0.5
                    mid = glm.normalize(mid) * radius
                    midpoints.append(mid)

                # Create four new triangles
                new_triangles = [
                    [triangle[0], midpoints[0], midpoints[2]],
                    [midpoints[0], triangle[1], midpoints[1]],
                    [midpoints[2], midpoints[1], triangle[2]],
                    [midpoints[0], midpoints[1], midpoints[2]],
                ]
                new_face_triangles.extend(new_triangles)

            new_faces.append(new_face_triangles)

        # Update faces and create new mesh
        self.faces = new_faces
        vertices = self.create_mesh()

        # Create new Mesh with updated vertices
        super().__init__(self.shader, vertices, self.model)
