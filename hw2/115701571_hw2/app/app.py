import copy

from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm

from .window import Window
from shape import (
    Renderable,
    BezierCurve,
    Polyline,
    PixelData,
    Pixel,
    C2Spline,
    CatmullRomSpline,
)
from util import Shader


class App(Window):
    def __init__(self):
        self.windowName: str = "hw2"
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
        glLineWidth(1.0)
        glPointSize(1.0)
        glEnable(GL_PROGRAM_POINT_SIZE)

        # Program context.

        self.bezierShader: Shader = Shader(
            vert="shader/bezier.vert.glsl",
            tesc="shader/bezier.tesc.glsl",
            tese="shader/bezier.tese.glsl",
            frag="shader/bezier.frag.glsl",
        )

        self.polyLineShader: Shader = Shader(
            vert="shader/polyline.vert.glsl",
            tesc=None,
            tese=None,
            frag="shader/polyline.frag.glsl",
        )

        self.pixelShader: Shader = Shader(
            vert="shader/pixel.vert.glsl",
            tesc=None,
            tese=None,
            frag="shader/pixel.frag.glsl",
        )

        self.catmullRomShader: Shader = Shader(
            vert="shader/catmullrom.vert.glsl",
            tesc="shader/catmullrom.tesc.glsl",
            tese="shader/catmullrom.tese.glsl",
            frag="shader/catmullrom.frag.glsl",
        )

        # Bezier curve control points
        self.bezierControlPoints: list[glm.vec2] = []
        self.drawingBezier: bool = False

        # CatmullRom curve control points
        self.catmullRomControlPoints: list[glm.vec2] = []
        self.drawingcatmullRom: bool = False

        # Renderers.
        self.bezierCurve: BezierCurve = BezierCurve(
            self.bezierShader, self.bezierControlPoints
        )
        self.previewPolyline: Polyline = Polyline(self.polyLineShader)
        self.pixelRenderer: Pixel = Pixel(self.pixelShader)
        self.c2_spline = C2Spline(self.bezierShader)
        self.catmullrom: CatmullRomSpline = CatmullRomSpline(
            self.catmullRomShader, self.catmullRomControlPoints
        )

        # Objects to render.
        self.shapes: list[Renderable] = []

        # Object attributes affected by GUI.
        self.animationEnabled: bool = True

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
            glClear(GL_COLOR_BUFFER_BIT)

            self.__render()

            # Check and call events and swap the buffers
            glfwSwapBuffers(self.window)
            glfwPollEvents()

    def renderControlPoints(self):
        self.pixelShader.use()
        self.pixelShader.setFloat("windowWidth", self.windowWidth)
        self.pixelShader.setFloat("windowHeight", self.windowHeight)

        # Convert control points to pixels with green color.
        # Render both bezier and catmullrom control points.
        pixels = []
        if self.bezierControlPoints:
            pixels = [
                PixelData(glm.vec2(cp.x, cp.y), glm.vec3(0.0, 1.0, 0.0))
                for cp in self.bezierControlPoints
            ]
        if self.catmullRomControlPoints:
            pixels = [
                PixelData(glm.vec2(cp.x, cp.y), glm.vec3(0.0, 1.0, 0.0))
                for cp in self.catmullRomControlPoints
            ]
        self.pixelRenderer.update_pixels(pixels)

        self.pixelRenderer.render(0, False)

    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)

        app.mousePos.x = xpos
        app.mousePos.y = app.windowHeight - ypos

        if app.drawingBezier and len(app.bezierControlPoints) > 0:
            preview_points = app.bezierControlPoints.copy()
            preview_points.append(copy.deepcopy(app.mousePos))
            app.previewPolyline.update_points(preview_points)
            # app.bezierControlPoints = copy.deepcopy(
            #     app.c2_spline.add_interpolation_point(copy.deepcopy(app.mousePos))
            # )

        if app.drawingcatmullRom and len(app.catmullRomControlPoints) > 0:
            preview_points = app.catmullRomControlPoints.copy()
            preview_points.append(copy.deepcopy(app.mousePos))
            app.previewPolyline.update_points(preview_points)
            app.catmullrom.update_points(preview_points)

        if app.mousePressed:
            # # Note: Must calculate offset first, then update lastMouseLeftPressPos.
            # # Also must invoke copy explicitly.
            # # C++: copy assign is copy; Python: it's reference!
            # glm::dvec2 offset = app.mousePos - app.lastMouseLeftPressPos;
            app.lastMouseLeftPressPos = copy.deepcopy(app.mousePos)

    def resetBezierDrawing(self):
        self.bezierControlPoints.clear()
        self.previewPolyline.update_points([])
        self.drawingBezier = True
        if self.c2_spline:
            self.shapes = []
            self.c2_spline = C2Spline(self.bezierShader)

    def resetCatmullRomDrawing(self):
        self.catmullRomControlPoints.clear()
        self.previewPolyline.update_points([])
        self.drawingcatmullRom = True
        if self.catmullrom:
            self.shapes = []
            self.catmullrom = CatmullRomSpline(
                self.catmullRomShader, self.catmullRomControlPoints
            )

    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)

    @staticmethod
    def __keyCallback(
        window: GLFWwindow, key: int, scancode: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if key == GLFW_KEY_1 and action == GLFW_PRESS:
            app.resetBezierDrawing()

        if key == GLFW_KEY_3 and action == GLFW_PRESS:
            app.resetCatmullRomDrawing()

    @staticmethod
    def __mouseButtonCallback(
        window: GLFWwindow, button: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if app.drawingBezier:
            if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
                app.bezierControlPoints = copy.deepcopy(
                    app.c2_spline.add_interpolation_point(copy.deepcopy(app.mousePos))
                )
                preview_points = app.bezierControlPoints.copy()
                app.previewPolyline.update_points(preview_points)

            elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
                app.bezierControlPoints = copy.deepcopy(
                    app.c2_spline.add_interpolation_point(
                        copy.deepcopy(app.mousePos), True
                    )
                )

                preview_points = app.bezierControlPoints.copy()
                app.previewPolyline.update_points(preview_points)

                app.shapes.append(app.previewPolyline)
                app.shapes.append(app.c2_spline)
                app.drawingBezier = False

        if app.drawingcatmullRom:
            if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
                app.catmullRomControlPoints.append(copy.deepcopy(app.mousePos))
                app.catmullrom.update_points(app.catmullRomControlPoints)
                preview_points = app.catmullRomControlPoints.copy()
                app.previewPolyline.update_points(preview_points)

            elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
                app.catmullRomControlPoints.append(copy.deepcopy(app.mousePos))
                app.catmullrom = CatmullRomSpline(
                    app.catmullRomShader, app.catmullRomControlPoints
                )

                preview_points = app.catmullRomControlPoints.copy()
                app.previewPolyline.update_points(preview_points)

                app.shapes.append(app.previewPolyline)
                app.shapes.append(app.catmullrom)
                app.drawingcatmullRom = False

    @staticmethod
    def __scrollCallback(window: GLFWwindow, xoffset: float, yoffset: float) -> None:
        pass

    @staticmethod
    def __perFrameTimeLogic(window: GLFWwindow) -> None:
        app: App = glfwGetWindowUserPointer(window)

        currentFrame: float = glfwGetTime()
        app.timeElapsedSinceLastFrame = currentFrame - app.lastFrameTimeStamp
        app.lastFrameTimeStamp = currentFrame

    @staticmethod
    def __processKeyInput(window: GLFWwindow) -> None:
        pass

    def __render(self) -> None:
        t: float = self.timeElapsedSinceLastFrame

        # Update all shader uniforms.
        self.polyLineShader.use()
        self.polyLineShader.setFloat("windowWidth", self.windowWidth)
        self.polyLineShader.setFloat("windowHeight", self.windowHeight)
        self.polyLineShader.setVec4("lineColor", glm.vec4(1.0, 0.0, 0.0, 1.0))

        self.bezierShader.use()
        self.bezierShader.setMat3(
            "model", glm.mat3(1.0)
        )  # Identity matrix, adjust if needed
        self.bezierShader.setFloat("windowWidth", self.windowWidth)
        self.bezierShader.setFloat("windowHeight", self.windowHeight)
        self.bezierShader.setVec4("bezierColor", glm.vec4(1.0, 1.0, 1.0, 1.0))

        self.catmullRomShader.use()
        self.catmullRomShader.setMat3("model", glm.mat3(1.0))
        self.catmullRomShader.setFloat("windowWidth", self.windowWidth)
        self.catmullRomShader.setFloat("windowHeight", self.windowHeight)
        self.catmullRomShader.setVec4("splineColor", glm.vec4(1.0, 1.0, 1.0, 1.0))

        if self.drawingBezier:
            self.previewPolyline.render(0, False)
            if len(self.bezierControlPoints) > 0:
                self.c2_spline.render(0, False)

        if self.drawingcatmullRom:
            self.previewPolyline.render(0, False)
            if len(self.catmullRomControlPoints) > 0:
                self.catmullrom.render(0, False)

        self.renderControlPoints()

        # Render all shapes.
        for s in self.shapes:
            s.render(t, self.animationEnabled)
