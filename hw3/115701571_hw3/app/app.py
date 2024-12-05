import copy
from enum import Enum

from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm

from .window import Window
from shape import Line, Mesh, Renderable, Tetrahedron, Icosahedron, Ellipsoid
from util import Camera, Shader


class DisplayMode(Enum):
    WIREFRAME = 1
    FLAT = 2
    SMOOTH = 3


class App(Window):
    def __init__(self):
        self.windowName: str = "hw3"
        self.windowWidth: int = 1000
        self.windowHeight: int = 1000
        super().__init__(self.windowWidth, self.windowHeight, self.windowName)

        # GLFW boilerplate.
        glfwSetWindowUserPointer(self.window, self)
        glfwSetCursorPosCallback(self.window, self.__cursorPosCallback)
        glfwSetFramebufferSizeCallback(self.window, self.__framebufferSizeCallback)
        glfwSetKeyCallback(self.window, self.__keyCallback)
        glfwSetMouseButtonCallback(self.window, self.__mouseButtonCallback)
        glfwSetScrollCallback(self.window, self.__scrollCallback)

        # Global OpenGL pipeline settings.
        glViewport(0, 0, self.windowWidth, self.windowHeight)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(2.0)
        glPointSize(1.0)

        # Only for 3D scenes!
        # Also remember to clear GL_DEPTH_BUFFER_BIT, or OpenGL won't display anything...
        glEnable(GL_DEPTH_TEST)

        # Program context.

        # Shaders.
        self.lineShader: Shader = Shader(
            vert="shader/line.vert.glsl",
            tesc=None,
            tese=None,
            frag="shader/line.frag.glsl",
        )

        self.meshShader: Shader = Shader(
            vert="shader/mesh.vert.glsl",
            tesc=None,
            tese=None,
            frag="shader/phong.frag.glsl",
        )

        # self.sphereShader: Shader = Shader(
        #     vert="shader/sphere.vert.glsl",
        #     tesc="shader/sphere.tesc.glsl",
        #     tese="shader/sphere.tese.glsl",
        #     frag="shader/phong.frag.glsl",
        # )

        # Objects to render.
        self.shapes: list[Renderable] = []

        self.axes = Line(
            self.lineShader,
            glm.array(
                glm.float32,
                # x-axis (red)
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                10.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                # y-axis (green)
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                10.0,
                0.0,
                0.0,
                1.0,
                0.0,
                # z-axis (blue)
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                10.0,
                0.0,
                0.0,
                1.0,
            ),
            glm.mat4(1.0),
        )

        self.showAxes = True
        self.current_mode = 1
        # self.shapes.append(
        #     Mesh(
        #         self.meshShader,
        #         glm.array(
        #             # dtype
        #             glm.float32,
        #             # pos (x y z)        # normal (x y z)   # color (r g b)
        #             -0.5,
        #             -0.5,
        #             0.0,
        #             0.0,
        #             0.0,
        #             1.0,
        #             1.0,
        #             0.0,
        #             0.0,
        #             0.5,
        #             -0.5,
        #             0.0,
        #             0.0,
        #             0.0,
        #             1.0,
        #             0.0,
        #             1.0,
        #             0.0,
        #             0.0,
        #             0.5,
        #             0.0,
        #             0.0,
        #             0.0,
        #             1.0,
        #             0.0,
        #             0.0,
        #             1.0,
        #         ),
        #         glm.rotate(
        #             glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 0.0)),
        #             glm.radians(45.0),
        #             glm.vec3(0.0, 1.0, 0.0),
        #         ),
        #     )
        # )

        self.flat_shapes = []
        # Tetrahedron
        self.flat_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/tetrahedron.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(-3.0, 0.0, 0.0)),
                use_smooth_normals=False,  # New parameter
            )
        )
        # Cube
        self.flat_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/cube.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                use_smooth_normals=False,
            )
        )
        # Octahedron
        self.flat_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/octahedron.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(3.0, 0.0, 0.0)),
                use_smooth_normals=False,
            )
        )
        self.flat_icosahedron = Icosahedron(
            self.meshShader,
            "var/icosahedron.txt",
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
            use_smooth_normals=False,
        )

        ellipsoid_scale = glm.vec3(1.5, 1.0, 0.8)  # Different scales for x, y, z
        self.flat_ellipsoid = Ellipsoid(
            self.meshShader,
            "var/icosahedron.txt",
            # ellipsoid_scale,
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
            use_smooth_normals=False,
        )

        # Create smooth-shaded versions
        self.smooth_shapes = []
        # Tetrahedron
        self.smooth_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/tetrahedron.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(-3.0, 0.0, 0.0)),
                use_smooth_normals=True,
            )
        )
        # Cube
        self.smooth_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/cube.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
                use_smooth_normals=True,
            )
        )
        # Octahedron
        self.smooth_shapes.append(
            Tetrahedron(
                self.meshShader,
                "var/octahedron.txt",
                glm.translate(glm.mat4(1.0), glm.vec3(3.0, 0.0, 0.0)),
                use_smooth_normals=True,
            )
        )

        self.smooth_icosahedron = Icosahedron(
            self.meshShader,
            "var/icosahedron.txt",
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
            use_smooth_normals=True,
        )

        self.smooth_ellipsoid = Ellipsoid(
            self.meshShader,
            "var/icosahedron.txt",
            # ellipsoid_scale,
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0)),
            use_smooth_normals=True,
        )

        # self.shapes.append(
        #     Sphere(
        #         self.sphereShader,
        #         glm.vec3(0.0, 0.0, 0.0),  # center (x y z)
        #         1.0,  # radius
        #         glm.vec3(1.0, 0.5, 0.31),  # color (r g b)
        #         glm.mat4(1.0),
        #     )
        # )
        self.displayMode = DisplayMode.FLAT  # Default to smooth shading

        # Viewing
        self.camera: Camera = Camera(glm.vec3(0.0, 0.0, 10.0))
        self.view: glm.mat4 = glm.mat4(1.0)
        self.projection: glm.mat4 = glm.mat4(1.0)

        # self.lightColor: glm.vec3 = glm.vec3(1.0, 1.0, 1.0)
        # self.lightPos: glm.vec3 = glm.vec3(10.0, 10.0, 10.0)

        self.lightPos: glm.vec3 = glm.vec3(5.0, 5.0, 10.0)
        self.lightColor: glm.vec3 = glm.vec3(1.0, 1.0, 1.0)

        # Frontend GUI
        self.timeElapsedSinceLastFrame: float = 0.0
        self.lastFrameTimeStamp: float = 0.0
        self.mousePressed: bool = False
        self.mousePos: glm.dvec2 = glm.dvec2(0.0, 0.0)

        self.debugMousePos: bool = False

        # Note lastMouseLeftClickPos is different from lastMouseLeftPressPos.
        # If you press left button (and hold it there) and move the mouse,
        # lastMouseLeftPressPos gets updated to the current mouse position
        # (while lastMouseLeftClickPos, if there is one, remains the original value).
        self.lastMouseLeftClickPos: glm.dvec2 = glm.dvec2(0.0, 0.0)
        self.lastMouseLeftPressPos: glm.dvec2 = glm.dvec2(0.0, 0.0)

    def run(self) -> None:
        while not glfwWindowShouldClose(self.window):
            # Per-frame logic
            self.__perFrameTimeLogic(self.window)
            self.__processKeyInput(self.window)

            # Send render commands to OpenGL server
            glClearColor(0.2, 0.3, 0.3, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.__render()

            # Check and call events and swap the buffers
            glfwSwapBuffers(self.window)
            glfwPollEvents()

    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)

        app.mousePos.x = xpos
        app.mousePos.y = app.windowHeight - ypos

        if app.debugMousePos:
            print(f"cursor @ {app.mousePos}")

        if app.mousePressed:
            # Note: Must calculate offset first, then update lastMouseLeftPressPos.
            # Also MUST explivitly use copy here!
            # C++: copy assign is copy; Python: it's reference!
            offset: glm.dvec2 = app.mousePos - app.lastMouseLeftPressPos

            if app.debugMousePos:
                print(f"mouse drag offset {offset}")

            app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)
            app.camera.processMouseMovement(offset.x, offset.y)

    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)

    @staticmethod
    def __keyCallback(
        window: GLFWwindow, key: int, scancode: int, action: int, mods: int
    ) -> None:
        if action != GLFW_PRESS:
            return

        app: App = glfwGetWindowUserPointer(window)

        if key == GLFW_KEY_1:
            app.current_mode = 1
            # Reset camera
            app.camera = Camera(glm.vec3(0.0, 0.0, 10.0))
        elif key == GLFW_KEY_2:
            app.current_mode = 2
            # Reset camera
            app.camera = Camera(glm.vec3(0.0, 0.0, 10.0))
        elif key == GLFW_KEY_F1:
            app.displayMode = DisplayMode.WIREFRAME
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        elif key == GLFW_KEY_F2:
            app.displayMode = DisplayMode.FLAT
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        elif key == GLFW_KEY_F4:
            app.displayMode = DisplayMode.SMOOTH
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        elif key == GLFW_KEY_X:
            app.showAxes = not app.showAxes
        elif key == GLFW_KEY_EQUAL and (mods & GLFW_MOD_SHIFT):  # This is the '+' key
            if app.current_mode == 2:  # Only subdivide in icosahedron mode
                app.flat_icosahedron.subdivide()
                app.smooth_icosahedron.subdivide()
        elif key == GLFW_KEY_3:
            app.current_mode = 3
            # Reset camera
            app.camera = Camera(glm.vec3(0.0, 0.0, 10.0))
        elif key == GLFW_KEY_EQUAL and (mods & GLFW_MOD_SHIFT):  # '+' key
            if app.current_mode == 2:  # Icosahedron mode
                app.flat_icosahedron.subdivide()
                app.smooth_icosahedron.subdivide()
            elif app.current_mode == 3:  # Ellipsoid mode
                app.flat_ellipsoid.subdivide()
                app.smooth_ellipsoid.subdivide()

    @staticmethod
    def __mouseButtonCallback(
        window: GLFWwindow, button: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                app.mousePressed = True

                # NOTE: MUST explivitly use copy here!
                # C++: copy assign is copy; Python: it's reference!
                app.lastMouseLeftClickPos = copy.deepcopy(app.mousePos)
                app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)

                if app.debugMousePos:
                    print(f"mouseLeftPress @ {app.mousePos}")

            elif action == GLFW_RELEASE:
                app.mousePressed = False

                if app.debugMousePos:
                    print(f"mouseLeftRelease @ {app.mousePos}")

    @staticmethod
    def __scrollCallback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:
        app: App = glfwGetWindowUserPointer(window)
        app.camera.processMouseScroll(yoffset)

    @staticmethod
    def __perFrameTimeLogic(window: GLFWwindow) -> None:
        app: App = glfwGetWindowUserPointer(window)

        currentFrame: float = glfwGetTime()
        app.timeElapsedSinceLastFrame = currentFrame - app.lastFrameTimeStamp
        app.lastFrameTimeStamp = currentFrame

    @staticmethod
    def __processKeyInput(window: GLFWwindow) -> None:
        # Camera control
        app: App = glfwGetWindowUserPointer(window)

        if glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kLeft, app.timeElapsedSinceLastFrame
            )

        if glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kRight, app.timeElapsedSinceLastFrame
            )

        if glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kBackWard, app.timeElapsedSinceLastFrame
            )

        if glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kForward, app.timeElapsedSinceLastFrame
            )

        if glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kUp, app.timeElapsedSinceLastFrame
            )

        if glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS:
            app.camera.processKeyboard(
                Camera.Movement.kDown, app.timeElapsedSinceLastFrame
            )

    def __render(self) -> None:
        t: float = self.timeElapsedSinceLastFrame

        # Update shader uniforms.
        self.view = self.camera.getViewMatrix()
        self.projection = glm.perspective(
            glm.radians(self.camera.zoom),
            self.windowWidth / self.windowHeight,
            0.01,
            100.0,
        )

        self.lineShader.use()
        self.lineShader.setMat4("view", self.view)
        self.lineShader.setMat4("projection", self.projection)

        self.meshShader.use()
        self.meshShader.setMat4("view", self.view)
        self.meshShader.setMat4("projection", self.projection)
        self.meshShader.setVec3("viewPos", self.camera.position)
        # self.meshShader.setVec3("lightPos", self.camera.position)
        self.meshShader.setVec3("lightPos", self.lightPos)
        self.meshShader.setVec3("lightColor", self.lightColor)
        self.meshShader.setInt(
            "displayMode", self.displayMode.value
        )  # Pass display mode to shader

        if self.showAxes:
            self.axes.render(t)

        if self.current_mode == 1:
            # Render basic shapes (tetrahedron, cube, octahedron)
            shapes_to_render = (
                self.flat_shapes
                if self.displayMode == DisplayMode.FLAT
                else self.smooth_shapes
            )
            for shape in shapes_to_render:
                shape.render(t)

        elif self.current_mode == 2:
            # Render icosahedron
            if self.displayMode == DisplayMode.FLAT:
                self.flat_icosahedron.render(t)
            else:
                self.smooth_icosahedron.render(t)

        elif self.current_mode == 3:
            # Render ellipsoid
            if self.displayMode == DisplayMode.FLAT:
                self.flat_ellipsoid.render(t)
            else:
                self.smooth_ellipsoid.render(t)
