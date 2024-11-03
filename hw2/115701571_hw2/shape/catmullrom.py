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
        self.selected_node_index = None

    def add_control_point(self, point: glm.vec2):
        self.control_points.append(point)
        self.update_vbo()

    def select_node(self, mouse_pos: glm.dvec2) -> bool:
        THRESHOLD = 10.0  # pixels
        closest_dist = float("inf")
        closest_idx = -1

        for i, point in enumerate(self.control_points):
            # Convert both vectors to the same type (vec2) before subtraction
            point_vec2 = glm.vec2(point.x, point.y)
            mouse_vec2 = glm.vec2(mouse_pos.x, mouse_pos.y)
            diff = point_vec2 - mouse_vec2
            dist = glm.length(diff)

            if dist < THRESHOLD and dist < closest_dist:
                closest_dist = dist
                closest_idx = i

        self.selected_node_index = closest_idx
        return closest_idx != -1

    def move_selected_node(self, new_pos: glm.dvec2):
        if self.selected_node_index == -1:
            return

        self.control_points[self.selected_node_index] = glm.vec2(new_pos.x, new_pos.y)
        self.update_vbo()

    def delete_selected_node(self):
        if self.selected_node_index == -1:
            return

        del self.control_points[self.selected_node_index]
        self.selected_node_index = -1
        self.update_vbo()

    def add_node_at_index(self, new_pos: glm.dvec2):
        if self.selected_node_index == -1:
            return

        self.control_points.insert(
            self.selected_node_index + 1, glm.vec2(new_pos.x, new_pos.y)
        )
        self.update_vbo()

    def update_points(self, points: list[glm.vec2]):
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
