import glm
import math
from typing import List, Optional
from OpenGL.GL import *
from collections import namedtuple

from shape import (
    Line,
    Mesh,
    Tetrahedron,
    Icosahedron,
    Ellipsoid,
    Parametric,
    Torus,
    Superquadric,
    Dodecahedron,
)
from util import Shader, Camera

Building = namedtuple("Building", ["model", "shape", "display_mode"])


class CityScene:
    def __init__(self, meshShader: Shader, parametricShader: Shader):
        self.meshShader = meshShader
        self.parametricShader = parametricShader
        self.buildings: List[Building] = []

        # Initialize camera with a farther viewing position
        self.camera = Camera(glm.vec3(0.0, 40.0, 80.0))
        self.camera.pitch = -30.0

        self.original_position = glm.vec3(0.0, 40.0, 80.0)
        self.original_front = self.camera.front
        self.original_up = self.camera.up
        self.original_pitch = -30.0
        self.original_yaw = -90.0

        # Increased animation radius to keep objects in view
        self.animation_radius = 100.0
        self.animation_height = 60.0

        self.light_pos = glm.vec3(0.0, 1000.0, 200.0)
        self.light_color = glm.vec3(1.0, 0.95, 0.8)

        self.is_animating = False
        self.animation_type = None
        self.animation_time = 0.0
        self.animation_duration = 5.0

        self.ground = self.create_ground()
        self.setup_city()

    def create_ground(self):
        ground_size = 10000.0
        vertices = glm.array(
            glm.float32,
            # Position (x, y, z)     Normal     Color (lighter gray)
            -ground_size,
            0.0,
            -ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
            ground_size,
            0.0,
            -ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
            ground_size,
            0.0,
            ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
            -ground_size,
            0.0,
            -ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
            ground_size,
            0.0,
            ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
            -ground_size,
            0.0,
            ground_size,
            0.0,
            1.0,
            0.0,
            0.35,
            0.35,
            0.35,
        )
        return Mesh(self.meshShader, vertices, glm.mat4(1.0))

    def setup_city(self):
        # Central skyscrapers
        base_height = 15.0
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 1:
                    height = base_height * 2
                else:
                    height = base_height * (0.8 + 0.4 * ((i + j) % 2))

                model = glm.translate(
                    glm.mat4(1.0), glm.vec3(i * 8 - 8, height / 2, j * 8 - 8)
                )
                model = glm.scale(model, glm.vec3(2.0, height, 2.0))
                skyscraper = Tetrahedron(
                    self.meshShader,
                    "var/cube.txt",
                    model,
                    use_smooth_normals=True,
                    color=glm.vec3(0.85, 0.95, 1.0),
                )
                self.buildings.append(Building(model, skyscraper, 1))

        # Science Center (Icosahedron)
        science_model = glm.translate(glm.mat4(1.0), glm.vec3(-25.0, 8.0, -25.0))
        science_model = glm.scale(science_model, glm.vec3(4.0, 4.0, 4.0))
        science = Icosahedron(
            self.meshShader,
            "var/icosahedron.txt",
            science_model,
            use_smooth_normals=True,
            color=glm.vec3(0.3, 0.6, 1.0),
        )
        self.buildings.append(Building(science_model, science, 1))

        # Museum (Ellipsoid)
        museum_model = glm.translate(glm.mat4(1.0), glm.vec3(25.0, 6.0, 25.0))
        museum = Ellipsoid(
            self.meshShader,
            "var/icosahedron.txt",
            glm.vec3(8.0, 4.0, 5.0),
            museum_model,
            use_smooth_normals=True,
            color=glm.vec3(0.9, 0.92, 0.95),
        )
        self.buildings.append(Building(museum_model, museum, 1))

        # Stadium (Cone)
        stadium_model = glm.translate(glm.mat4(1.0), glm.vec3(-25.0, 0.0, 25.0))
        stadium_model = glm.scale(stadium_model, glm.vec3(6.0, 3.0, 6.0))
        stadium = Parametric(
            self.parametricShader,
            2,  # cone type
            glm.vec3(0.85, 0.85, 0.83),
            stadium_model,
        )
        self.buildings.append(Building(stadium_model, stadium, 2))

        # Convention Center (Sphere)
        convention_model = glm.translate(glm.mat4(1.0), glm.vec3(25.0, 5.0, -25.0))
        convention_model = glm.scale(convention_model, glm.vec3(5.0, 5.0, 5.0))
        convention = Parametric(
            self.parametricShader,
            0,  # sphere type
            glm.vec3(0.95, 0.95, 0.98),  # Bright metallic
            convention_model,
        )
        self.buildings.append(Building(convention_model, convention, 2))

        # Art Structure (Torus)
        art_model = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 3.0, -25.0))
        art_model = glm.scale(art_model, glm.vec3(3.0, 3.0, 3.0))
        art_model = glm.rotate(art_model, glm.radians(90.0), glm.vec3(1.0, 0.0, 0.0))
        art = Torus(
            self.meshShader,
            2.0,
            0.5,
            glm.vec3(0.85, 0.55, 0.25),  # Rich bronze
            art_model,
        )
        self.buildings.append(Building(art_model, art, 1))

        # Modern Art Center (Superquadric)
        modern_model = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 5.0, 25.0))
        modern_model = glm.scale(modern_model, glm.vec3(5.0, 5.0, 5.0))
        modern = Superquadric(
            self.parametricShader,
            2.0,
            2.0,
            glm.vec3(1.0, 0.3, 0.4),  # Vivid red
            modern_model,
        )
        self.buildings.append(Building(modern_model, modern, 2))

        # Central Tower (Dodecahedron)
        tower_model = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 25.0, 0.0))
        tower_model = glm.scale(tower_model, glm.vec3(2.0, 4.0, 2.0))
        tower = Dodecahedron(
            self.meshShader,
            "var/dodecahedron.txt",
            tower_model,
            use_smooth_normals=True,
            color=glm.vec3(0.95, 0.95, 0.98),
        )
        self.buildings.append(Building(tower_model, tower, 1))

    def reset_camera(self):
        """Reset camera to its original state"""
        self.camera.position = self.original_position
        self.camera.front = self.original_front
        self.camera.up = self.original_up
        self.camera.pitch = self.original_pitch
        self.camera.yaw = self.original_yaw

        # Force update of camera vectors
        self.camera._Camera__updateCameraVectors()

    def start_animation(self, animation_type: str):
        self.is_animating = True
        self.animation_type = animation_type
        self.animation_time = 0.0

        # Store starting position and calculate target start position
        self.start_pos = glm.vec3(self.camera.position)
        radius = 100.0

        if animation_type == "H":
            self.target_start_pos = glm.vec3(radius, 40.0, 0.0)
        else:  # "V"
            self.target_start_pos = glm.vec3(0.0, 40.0, radius)

        self.in_transition = True
        self.transition_duration = 1.0  # Time to move to start position
        self.transition_time = 0.0

    def update(self, delta_time: float):
        if not self.is_animating:
            return

        target = glm.vec3(0.0, 15.0, 0.0)
        up_vector = glm.vec3(0.0, 1.0, 0.0)

        if self.in_transition:
            self.transition_time += delta_time
            progress = min(self.transition_time / self.transition_duration, 1.0)

            self.camera.position = (
                self.start_pos + (self.target_start_pos - self.start_pos) * progress
            )

            if progress >= 1.0:
                self.in_transition = False
                self.animation_time = 0.0
        else:
            self.animation_time += delta_time
            progress = self.animation_time / self.animation_duration

            if progress >= 1.0:
                self.is_animating = False
                return

            angle = progress * 2.0 * math.pi
            radius = 100.0

            if self.animation_type == "H":
                x = radius * math.cos(angle)
                z = radius * math.sin(angle)
                y = 40.0
                self.camera.position = glm.vec3(x, y, z)
                up_vector = glm.vec3(0.0, 1.0, 0.0)
            else:  # "V"
                y = 40.0 + radius * math.sin(angle)
                z = radius * math.cos(angle)
                self.camera.position = glm.vec3(0.0, y, z)

                # Use local up vector based on position in loop
                if math.pi / 2 <= angle <= 3 * math.pi / 2:
                    up_vector = glm.vec3(
                        0.0, -1.0, 0.0
                    )  # Invert up vector when upside down
                else:
                    up_vector = glm.vec3(0.0, 1.0, 0.0)

        look_matrix = glm.lookAt(self.camera.position, target, up_vector)

        self.camera.front = -glm.vec3(
            look_matrix[0][2], look_matrix[1][2], look_matrix[2][2]
        )
        self.camera.right = glm.vec3(
            look_matrix[0][0], look_matrix[1][0], look_matrix[2][0]
        )
        self.camera.up = glm.cross(self.camera.right, self.camera.front)

    def render(self, time_elapsed: float, display_mode: int):
        # Update animation if active
        self.update(time_elapsed)

        # Setup view and projection matrices
        view = self.camera.getViewMatrix()
        projection = glm.perspective(
            glm.radians(self.camera.zoom),
            1000.0 / 1000.0,
            0.1,
            1000.0,  # Increased for larger ground plane
        )

        # Render ground first
        self.meshShader.use()
        self.meshShader.setMat4("view", view)
        self.meshShader.setMat4("projection", projection)
        self.meshShader.setVec3("viewPos", self.camera.position)
        self.meshShader.setVec3("lightPos", self.light_pos)
        self.meshShader.setVec3("lightColor", self.light_color)
        self.meshShader.setInt("displayMode", display_mode)
        self.ground.render(time_elapsed)

        # Render mesh shader objects
        self.meshShader.use()
        self.meshShader.setMat4("view", view)
        self.meshShader.setMat4("projection", projection)
        self.meshShader.setVec3("viewPos", self.camera.position)
        self.meshShader.setVec3("lightPos", self.light_pos)
        self.meshShader.setVec3("lightColor", self.light_color)
        self.meshShader.setInt("displayMode", display_mode)

        # Render parametric shader objects
        self.parametricShader.use()
        self.parametricShader.setMat4("view", view)
        self.parametricShader.setMat4("projection", projection)
        self.parametricShader.setVec3("viewPos", self.camera.position)
        self.parametricShader.setVec3("lightPos", self.light_pos)
        self.parametricShader.setVec3("lightColor", self.light_color)

        # Render all buildings
        for building in self.buildings:
            if building.display_mode == 1:
                self.meshShader.use()
            else:
                self.parametricShader.use()
            building.shape.render(time_elapsed)
