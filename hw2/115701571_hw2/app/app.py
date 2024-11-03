import copy
from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm

from .window import Window
from shape import (
    BezierCurve,
    Polyline,
    PixelData,
    Pixel,
    C2Spline,
    CatmullRomSpline,
)
from util import Shader, SplineIO


class AppState:
    def __init__(self):
        # Drawing states
        self.drawing_bezier = False
        self.editing_bezier = False
        self.drawing_catmullrom = False
        self.editing_catmullrom = False

        # Input states
        self.mouse_pressed = False

        # Application states
        self.animation_enabled = True
        self.debug_mouse_pos = False


class App(Window):
    def __init__(self):
        # Window setup
        self.window_name = "hw2"
        self.window_width = 1000
        self.window_height = 1000
        super().__init__(self.window_width, self.window_height, self.window_name)

        # Initialize all components
        self._init_glfw()
        self._init_opengl()
        self._init_shaders()
        self._init_state()
        self._init_renderers()

    def _init_glfw(self):
        glfwSetWindowUserPointer(self.window, self)
        glfwSetCursorPosCallback(self.window, self.__cursorPosCallback)
        glfwSetFramebufferSizeCallback(self.window, self.__framebufferSizeCallback)
        glfwSetKeyCallback(self.window, self.__keyCallback)
        glfwSetMouseButtonCallback(self.window, self.__mouseButtonCallback)
        glfwSetScrollCallback(self.window, self.__scrollCallback)

    def _init_opengl(self):
        glViewport(0, 0, self.window_width, self.window_height)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glPointSize(1.0)
        glEnable(GL_PROGRAM_POINT_SIZE)

    def _init_shaders(self):
        self.shaders = {
            "bezier": Shader(
                vert="shader/bezier.vert.glsl",
                tesc="shader/bezier.tesc.glsl",
                tese="shader/bezier.tese.glsl",
                frag="shader/bezier.frag.glsl",
            ),
            "polyline": Shader(
                vert="shader/polyline.vert.glsl",
                tesc=None,
                tese=None,
                frag="shader/polyline.frag.glsl",
            ),
            "pixel": Shader(
                vert="shader/pixel.vert.glsl",
                tesc=None,
                tese=None,
                frag="shader/pixel.frag.glsl",
            ),
            "catmullrom": Shader(
                vert="shader/catmullrom.vert.glsl",
                tesc="shader/catmullrom.tesc.glsl",
                tese="shader/catmullrom.tese.glsl",
                frag="shader/catmullrom.frag.glsl",
            ),
        }

    def _init_state(self):
        # Application state
        self.state = AppState()

        # Control points for different curves
        self.bezier_control_points = []
        self.catmullrom_control_points = []

        # Mouse tracking
        self.mouse_pos = glm.dvec2(0.0, 0.0)
        self.last_mouse_left_click_pos = glm.dvec2(0.0, 0.0)
        self.last_mouse_left_press_pos = glm.dvec2(0.0, 0.0)

        # Time tracking
        self.time_elapsed_since_last_frame = 0.0
        self.last_frame_time_stamp = 0.0

        # Render objects
        self.shapes = []

    def _init_renderers(self):
        # Initialize curve renderers
        self.bezier_curve = BezierCurve(
            self.shaders["bezier"], self.bezier_control_points
        )
        self.c2_spline = C2Spline(self.shaders["bezier"])
        self.catmullrom = CatmullRomSpline(
            self.shaders["catmullrom"], self.catmullrom_control_points
        )

        # Initialize utility renderers
        self.preview_polyline = Polyline(self.shaders["polyline"])
        self.pixel_renderer = Pixel(self.shaders["pixel"])

    def _update_shader_uniforms(self):
        # Common settings for all shaders
        common_settings = {
            "windowWidth": self.window_width,
            "windowHeight": self.window_height,
            "model": glm.mat3(1.0),
        }

        # Update polyline shader
        self.shaders["polyline"].use()
        for key, value in common_settings.items():
            if isinstance(value, (int, float)):
                self.shaders["polyline"].setFloat(key, value)
            elif isinstance(value, glm.mat3):
                self.shaders["polyline"].setMat3(key, value)
        self.shaders["polyline"].setVec4("lineColor", glm.vec4(1.0, 0.0, 0.0, 1.0))

        # Update bezier and catmullrom shaders
        for shader_name in ["bezier", "catmullrom"]:
            self.shaders[shader_name].use()
            for key, value in common_settings.items():
                if isinstance(value, (int, float)):
                    self.shaders[shader_name].setFloat(key, value)
                elif isinstance(value, glm.mat3):
                    self.shaders[shader_name].setMat3(key, value)
            # Set appropriate color uniform for each shader
            color_uniform = "bezierColor" if shader_name == "bezier" else "splineColor"
            self.shaders[shader_name].setVec4(
                color_uniform, glm.vec4(1.0, 1.0, 1.0, 1.0)
            )

    def run(self) -> None:
        while not glfwWindowShouldClose(self.window):
            # Update time and handle input
            self.__perFrameTimeLogic(self.window)
            self.__processKeyInput(self.window)

            # Clear frame
            glClearColor(0.2, 0.3, 0.3, 1.0)
            glClear(GL_COLOR_BUFFER_BIT)

            # Render frame
            self.__render()

            # Swap buffers and poll events
            glfwSwapBuffers(self.window)
            glfwPollEvents()

    def reset_bezier_drawing(self):
        self._reset_common()
        self.state.drawing_bezier = True
        self.c2_spline = C2Spline(self.shaders["bezier"])

    def reset_catmullrom_drawing(self):
        self._reset_common()
        self.state.drawing_catmullrom = True
        self.catmullrom = CatmullRomSpline(
            self.shaders["catmullrom"], self.catmullrom_control_points
        )

    def _reset_common(self):
        # Clear control points
        self.bezier_control_points.clear()
        self.catmullrom_control_points.clear()
        self.preview_polyline.update_points([])

        # Reset state
        self.state = AppState()
        self.shapes.clear()

    def _handle_bezier_mouse_press(self, is_right_click: bool):
        point = copy.deepcopy(self.mouse_pos)

        # Add point to spline
        self.bezier_control_points = copy.deepcopy(
            self.c2_spline.add_interpolation_point(point, is_right_click)
        )

        # Update preview
        preview_points = self.bezier_control_points.copy()
        self.preview_polyline.update_points(preview_points)

        # Finalize if right click
        if is_right_click:
            self.shapes.append(self.preview_polyline)
            self.shapes.append(self.c2_spline)
            self.state.drawing_bezier = False
            self.state.editing_bezier = True

    def _handle_catmullrom_mouse_press(self, is_right_click: bool):
        point = copy.deepcopy(self.mouse_pos)

        # Add point to spline
        self.catmullrom_control_points.append(point)
        self.catmullrom.update_points(self.catmullrom_control_points)

        # Update preview
        preview_points = self.catmullrom_control_points.copy()
        self.preview_polyline.update_points(preview_points)

        # Finalize if right click
        if is_right_click:
            self.catmullrom = CatmullRomSpline(
                self.shaders["catmullrom"], self.catmullrom_control_points
            )
            self.shapes.append(self.preview_polyline)
            self.shapes.append(self.catmullrom)
            self.state.drawing_catmullrom = False
            self.state.editing_catmullrom = True

    def render_control_points(self):
        # Setup shader
        self.shaders["pixel"].use()
        self.shaders["pixel"].setFloat("windowWidth", self.window_width)
        self.shaders["pixel"].setFloat("windowHeight", self.window_height)

        pixels = []

        # Add bezier control points
        if self.bezier_control_points:
            for i, cp in enumerate(self.bezier_control_points):
                color = (
                    glm.vec3(0.0, 0.0, 1.0)
                    if (self.c2_spline and i == self.c2_spline.selected_node_index)
                    else glm.vec3(0.0, 1.0, 0.0)
                )
                pixels.append(PixelData(glm.vec2(cp.x, cp.y), color))

        # Add Catmull-Rom control points
        if self.catmullrom_control_points:
            for i, cp in enumerate(self.catmullrom_control_points):
                color = (
                    glm.vec3(0.0, 0.0, 1.0)
                    if (self.catmullrom and i == self.catmullrom.selected_node_index)
                    else glm.vec3(0.0, 1.0, 0.0)
                )
                pixels.append(PixelData(glm.vec2(cp.x, cp.y), color))

        # Render all control points
        self.pixel_renderer.update_pixels(pixels)
        self.pixel_renderer.render(0, False)

    def __render(self) -> None:
        # Update timing
        t: float = self.time_elapsed_since_last_frame

        # Update shader uniforms
        self._update_shader_uniforms()

        # Render active curve preview
        if self.state.drawing_bezier:
            self.preview_polyline.render(0, False)
            if len(self.bezier_control_points) > 0:
                self.c2_spline.render(0, False)

        if self.state.drawing_catmullrom:
            self.preview_polyline.render(0, False)
            if len(self.catmullrom_control_points) > 0:
                self.catmullrom.render(0, False)

        # Render control points
        self.render_control_points()

        # Render all shapes
        for shape in self.shapes:
            shape.render(t, self.state.animation_enabled)

    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)
        # Update mouse position, converting to our coordinate system
        app.mouse_pos.x = xpos
        app.mouse_pos.y = app.window_height - ypos

        app._handle_cursor_movement()

    def _handle_cursor_movement(self):
        # Handle Bezier curve editing
        if (
            self.state.editing_bezier
            and self.state.mouse_pressed
            and self.c2_spline.selected_node_index != -1
        ):
            self._update_bezier_node_position()

        # Handle Catmull-Rom spline editing
        if (
            self.state.editing_catmullrom
            and self.state.mouse_pressed
            and self.catmullrom.selected_node_index != -1
        ):
            self._update_catmullrom_node_position()

        # Handle Bezier curve drawing preview
        if self.state.drawing_bezier and len(self.bezier_control_points) > 0:
            self._update_bezier_preview()

        # Handle Catmull-Rom drawing preview
        if self.state.drawing_catmullrom and len(self.catmullrom_control_points) > 0:
            self._update_catmullrom_preview()

        # Update last mouse position if pressed
        if self.state.mouse_pressed:
            self.last_mouse_left_press_pos = copy.deepcopy(self.mouse_pos)

    def _update_bezier_node_position(self):
        self.c2_spline.move_selected_node(copy.deepcopy(self.mouse_pos))
        self.bezier_control_points = copy.deepcopy(self.c2_spline.control_points)
        self.preview_polyline.update_points(self.bezier_control_points)

    def _update_catmullrom_node_position(self):
        self.catmullrom.move_selected_node(copy.deepcopy(self.mouse_pos))
        self.catmullrom_control_points = copy.deepcopy(self.catmullrom.control_points)
        self.preview_polyline.update_points(self.catmullrom_control_points)

    def _update_bezier_preview(self):
        self.c2_spline.update_preview(copy.deepcopy(self.mouse_pos))
        preview_points = self.bezier_control_points.copy()
        preview_points.append(copy.deepcopy(self.mouse_pos))
        self.preview_polyline.update_points(preview_points)

    def _update_catmullrom_preview(self):
        preview_points = self.catmullrom_control_points.copy()
        preview_points.append(copy.deepcopy(self.mouse_pos))
        self.preview_polyline.update_points(preview_points)
        self.catmullrom.update_points(preview_points)

    @staticmethod
    def __mouseButtonCallback(
        window: GLFWwindow, button: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        # Handle drawing modes
        if app.state.drawing_bezier:
            if action == GLFW_PRESS:
                app._handle_bezier_mouse_press(button == GLFW_MOUSE_BUTTON_RIGHT)
        elif app.state.drawing_catmullrom:
            if action == GLFW_PRESS:
                app._handle_catmullrom_mouse_press(button == GLFW_MOUSE_BUTTON_RIGHT)

        # Handle editing modes
        elif app.state.editing_bezier:
            app._handle_editing_bezier_mouse_event(button, action)
        elif app.state.editing_catmullrom:
            app._handle_editing_catmullrom_mouse_event(button, action)

    def _handle_editing_bezier_mouse_event(self, button: int, action: int):
        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                if self.c2_spline.select_node(copy.deepcopy(self.mouse_pos)):
                    self.state.mouse_pressed = True
            elif action == GLFW_RELEASE:
                self.state.mouse_pressed = False

    def _handle_editing_catmullrom_mouse_event(self, button: int, action: int):
        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                if self.catmullrom.select_node(copy.deepcopy(self.mouse_pos)):
                    self.state.mouse_pressed = True
            elif action == GLFW_RELEASE:
                self.state.mouse_pressed = False

    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)

    @staticmethod
    def __scrollCallback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:
        pass

    @staticmethod
    def __perFrameTimeLogic(window: GLFWwindow) -> None:
        app: App = glfwGetWindowUserPointer(window)
        currentFrame: float = glfwGetTime()
        app.time_elapsed_since_last_frame = currentFrame - app.last_frame_time_stamp
        app.last_frame_time_stamp = currentFrame

    @staticmethod
    def __processKeyInput(window: GLFWwindow) -> None:
        pass

    @staticmethod
    def __keyCallback(
        window: GLFWwindow, key: int, scancode: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if action == GLFW_PRESS:
            app._handle_key_press(key, mods)

    def _handle_key_press(self, key: int, mods: int):
        # Mode switching keys
        if key == GLFW_KEY_1:
            self.reset_bezier_drawing()
        elif key == GLFW_KEY_3:
            self.reset_catmullrom_drawing()

        # Node manipulation keys
        elif key == GLFW_KEY_DELETE:
            self._handle_delete_node()
        elif key == GLFW_KEY_INSERT:
            self._handle_insert_node()

        # File operation keys
        elif key == GLFW_KEY_S and (mods & GLFW_MOD_CONTROL):
            self._handle_save()
        elif key == GLFW_KEY_L and (mods & GLFW_MOD_CONTROL):
            self._handle_load()

    def _handle_delete_node(self):
        if self.state.editing_bezier:
            if self.c2_spline.delete_selected_node():
                self.bezier_control_points = copy.deepcopy(
                    self.c2_spline.control_points
                )
                self.preview_polyline.update_points(self.bezier_control_points)
        elif self.state.editing_catmullrom:
            self.catmullrom.delete_selected_node()
            self.catmullrom_control_points = copy.deepcopy(
                self.catmullrom.control_points
            )
            self.preview_polyline.update_points(self.catmullrom_control_points)

    def _handle_insert_node(self):
        new_pos = glm.vec2(self.mouse_pos.x, self.mouse_pos.y)

        if self.state.editing_bezier:
            if self.c2_spline.insert_node(new_pos):
                self.bezier_control_points = copy.deepcopy(
                    self.c2_spline.control_points
                )
                self.preview_polyline.update_points(self.bezier_control_points)
        elif self.state.editing_catmullrom:
            self.catmullrom.add_node_at_index(self.mouse_pos)
            self.catmullrom_control_points = copy.deepcopy(
                self.catmullrom.control_points
            )
            self.preview_polyline.update_points(self.catmullrom_control_points)

    def _handle_save(self):
        CONFIG_PATH = "etc/config.txt"

        if self.state.editing_bezier:
            SplineIO.save_spline(
                CONFIG_PATH, self.bezier_control_points, True
            )  # is_c2=True
        elif self.state.editing_catmullrom:
            SplineIO.save_spline(
                CONFIG_PATH, self.catmullrom_control_points, False
            )  # is_c2=False

    def _handle_load(self):
        CONFIG_PATH = "etc/config.txt"
        result = SplineIO.load_spline(CONFIG_PATH)

        if result is None:
            return

        control_points, is_2d, is_c2 = result
        self.shapes.clear()

        if is_c2:
            self._load_bezier_spline(control_points)
        else:
            self._load_catmullrom_spline(control_points)

    def _load_bezier_spline(self, control_points):
        # Reset state and initialize new curve
        self.reset_bezier_drawing()
        self.bezier_control_points = control_points
        self.c2_spline = C2Spline(self.shaders["bezier"])

        # Update curve and preview
        self.c2_spline.update_points(control_points)
        self.preview_polyline.update_points(control_points)

        # Add to render list
        self.shapes.extend([self.preview_polyline, self.c2_spline])

        # Update state
        self.state.drawing_bezier = False
        self.state.editing_bezier = True

    def _load_catmullrom_spline(self, control_points):
        # Reset state and initialize new curve
        self.reset_catmullrom_drawing()
        self.catmullrom_control_points = control_points
        self.catmullrom = CatmullRomSpline(self.shaders["catmullrom"], control_points)

        # Update preview
        self.preview_polyline.update_points(control_points)

        # Add to render list
        self.shapes.extend([self.preview_polyline, self.catmullrom])

        # Update state
        self.state.drawing_catmullrom = False
        self.state.editing_catmullrom = True
