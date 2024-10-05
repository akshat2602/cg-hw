import copy

from OpenGL.GL import *
from glfw.GLFW import *
from glfw import _GLFWwindow as GLFWwindow
import glm

from .window import Window
from shape import Pixel, Renderable
from util import Shader


class App(Window):
    def __init__(self):
        self.windowName: str = "hw1"
        self.windowWidth: int = 1000
        self.windowHeight: int = 1000

        self.mode: int = 0
        self.polyline_points: list[glm.dvec2] = []
        self.is_drawing_polyline: bool = False
        self.is_drawing_circle: bool = False
        self.is_drawing_ellipse: bool = False
        self.shift_pressed: bool = False
        self.circle_center: glm.dvec2 = glm.dvec2(0.0, 0.0)
        self.ellipse_center: glm.dvec2 = glm.dvec2(0.0, 0.0)

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

        # Program context.

        # Shaders.
        self.pixelShader: Shader = Shader(
            vert="shader/pixel.vert.glsl",
            tesc=None,
            tese=None,
            frag="shader/pixel.frag.glsl",
        )

        # Shapes.
        self.shapes: list[Renderable] = []
        self.shapes.append(Pixel(self.pixelShader))

        # Frontend GUI
        self.showPreview: bool = False

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

    @staticmethod
    def __cursorPosCallback(window: GLFWwindow, xpos: float, ypos: float) -> None:
        app: App = glfwGetWindowUserPointer(window)

        app.mousePos.x = xpos
        app.mousePos.y = app.windowHeight - ypos

        if app.mode == 1 and app.showPreview:
            pixel: Pixel = app.shapes[0]
            pixel.path.clear()
            app.__bresenhamLine(
                pixel.path,
                int(app.lastMouseLeftClickPos.x),
                int(app.lastMouseLeftClickPos.y),
                int(app.mousePos.x),
                int(app.mousePos.y),
            )
            pixel.dirty = True
        elif app.mode == 3 and app.showPreview and app.is_drawing_polyline:
            pixel: Pixel = app.shapes[0]
            pixel.path.clear()

            # Draw existing poly-line segments
            for i in range(len(app.polyline_points) - 1):
                app.__bresenhamLine(
                    pixel.path,
                    int(app.polyline_points[i].x),
                    int(app.polyline_points[i].y),
                    int(app.polyline_points[i + 1].x),
                    int(app.polyline_points[i + 1].y),
                )

            # Draw preview line from last point to current mouse position
            if app.polyline_points:
                last_point = app.polyline_points[-1]
                app.__bresenhamLine(
                    pixel.path,
                    int(last_point.x),
                    int(last_point.y),
                    int(app.mousePos.x),
                    int(app.mousePos.y),
                )

            pixel.dirty = True

        elif app.mode == 4 and app.showPreview:
            pixel: Pixel = app.shapes[0]
            pixel.path.clear()

            if app.is_drawing_circle:
                r = int(glm.distance(app.circle_center, app.mousePos))
                app.__midpoint_circle(
                    app.shapes[0].path,
                    x0=int(app.circle_center.x),
                    y0=int(app.circle_center.y),
                    r=r,
                )
            elif app.is_drawing_ellipse:
                a = int(abs(app.mousePos.x - app.ellipse_center.x))
                b = int(abs(app.mousePos.y - app.ellipse_center.y))
                app.__midpoint_ellipse(
                    app.shapes[0].path,
                    x0=int(app.ellipse_center.x),
                    y0=int(app.ellipse_center.y),
                    a=a,
                    b=b,
                )

            pixel.dirty = True

    @staticmethod
    def __framebufferSizeCallback(window: GLFWwindow, width: int, height: int) -> None:
        glViewport(0, 0, width, height)

    @staticmethod
    def __keyCallback(
        window: GLFWwindow, key: int, scancode: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)
        if key == GLFW_KEY_1 and action == GLFW_PRESS:
            app.mode = 1
            app.showPreview = False
            app.shapes[0].path.clear()
            app.shapes[0].dirty = True
        elif key == GLFW_KEY_3 and action == GLFW_PRESS:
            app.mode = 3
            app.showPreview = False
            app.shapes[0].path.clear()
            app.polyline_points.clear()
            app.is_drawing_polyline = False
            app.shapes[0].dirty = True
        elif key == GLFW_KEY_4 and action == GLFW_PRESS:
            app.mode = 4
            app.showPreview = False
            app.shapes[0].path.clear()
            app.shapes[0].dirty = True
            app.is_drawing_circle = False
            app.is_drawing_ellipse = False
        elif key == GLFW_KEY_LEFT_SHIFT or key == GLFW_KEY_RIGHT_SHIFT:
            app.shift_pressed = action != GLFW_RELEASE

    @staticmethod
    def __mouseButtonCallback(
        window: GLFWwindow, button: int, action: int, mods: int
    ) -> None:
        app: App = glfwGetWindowUserPointer(window)

        if app.mode == 1:
            if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
                app.lastMouseLeftClickPos = copy.deepcopy(app.mousePos)
                app.showPreview = True
            elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
                app.showPreview = False
                app.__bresenhamLine(
                    app.shapes[0].path,
                    int(app.lastMouseLeftClickPos.x),
                    int(app.lastMouseLeftClickPos.y),
                    int(app.mousePos.x),
                    int(app.mousePos.y),
                )
                app.shapes[0].dirty = True

        elif app.mode == 3:
            if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
                if not app.is_drawing_polyline:
                    app.polyline_points.clear()
                    app.is_drawing_polyline = True
                app.polyline_points.append(copy.deepcopy(app.mousePos))
                app.showPreview = True
            elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
                app.polyline_points.append(copy.deepcopy(app.mousePos))
                app.showPreview = False
                app.is_drawing_polyline = False

                # Draw the final poly-line or polygon
                app.shapes[0].path.clear()
                for i in range(len(app.polyline_points) - 1):
                    app.__bresenhamLine(
                        app.shapes[0].path,
                        int(app.polyline_points[i].x),
                        int(app.polyline_points[i].y),
                        int(app.polyline_points[i + 1].x),
                        int(app.polyline_points[i + 1].y),
                    )

                # If 'C' key is held, close the polygon
                if glfwGetKey(window, GLFW_KEY_C) == GLFW_PRESS:
                    app.__bresenhamLine(
                        app.shapes[0].path,
                        int(app.polyline_points[-1].x),
                        int(app.polyline_points[-1].y),
                        int(app.polyline_points[0].x),
                        int(app.polyline_points[0].y),
                    )

                app.shapes[0].dirty = True

        elif app.mode == 4:
            if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
                if app.shift_pressed:
                    app.is_drawing_circle = True
                    app.is_drawing_ellipse = False
                    app.circle_center = copy.deepcopy(app.mousePos)
                else:
                    app.is_drawing_circle = False
                    app.is_drawing_ellipse = True
                    app.ellipse_center = copy.deepcopy(app.mousePos)
                app.showPreview = True
            elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
                app.showPreview = False
                if app.is_drawing_circle:
                    r = int(glm.distance(app.circle_center, app.mousePos))
                    app.__midpoint_circle(
                        app.shapes[0].path,
                        x0=int(app.circle_center.x),
                        y0=int(app.circle_center.y),
                        r=r,
                    )
                elif app.is_drawing_ellipse:
                    a = int(abs(app.mousePos.x - app.ellipse_center.x))
                    b = int(abs(app.mousePos.y - app.ellipse_center.y))
                    app.__midpoint_ellipse(
                        app.shapes[0].path,
                        x0=int(app.ellipse_center.x),
                        y0=int(app.ellipse_center.y),
                        a=a,
                        b=b,
                    )
                app.shapes[0].dirty = True

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

    @staticmethod
    def __bresenhamLine(
        path: list[glm.float32], x0: int, y0: int, x1: int, y1: int
    ) -> None:
        """
        Bresenham line-drawing algorithm for line (x0, y0) -> (x1, y1) in screen space,
        given that its slope m satisfies 0.0 <= m <= 1.0 and that (x0, y0) is the start position.
        All pixels on this line are appended to path
        (a list of glm.float32s, each five glm.float32s constitute a pixel (x y) (r g b).)
        P.S. Returning a view of path is more Pythonic,
        however, we still modify the argument for consistency with the C++ version...
        """
        dx = x1 - x0
        dy = y1 - y0

        if dx == 0:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                path.extend([x0, y, 1.0, 1.0, 1.0])
            return

        steep = abs(dy) > abs(dx)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0

        y_step = 1 if dy > 0 else -1

        d = 2 * abs(dy) - dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                path.extend([y, x, 1.0, 1.0, 1.0])
            else:
                path.extend([x, y, 1.0, 1.0, 1.0])

            if d > 0:
                y += y_step
                d -= 2 * dx
            d += 2 * abs(dy)

    @staticmethod
    def __midpoint_circle(path: list[glm.float32], x0: int, y0: int, r: int) -> None:
        x = 0
        y = r
        d = 1 - r

        while x <= y:
            path.extend([x0 + x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 + x, y0 - y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 - y, 1.0, 1.0, 1.0])
            path.extend([x0 + y, y0 + x, 1.0, 1.0, 1.0])
            path.extend([x0 - y, y0 + x, 1.0, 1.0, 1.0])
            path.extend([x0 + y, y0 - x, 1.0, 1.0, 1.0])
            path.extend([x0 - y, y0 - x, 1.0, 1.0, 1.0])

            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    @staticmethod
    def __midpoint_ellipse(
        path: list[glm.float32], x0: int, y0: int, a: int, b: int
    ) -> None:
        x = 0
        y = b
        d1 = b * b - a * a * b + 0.25 * a * a
        dx = 2 * b * b * x
        dy = 2 * a * a * y

        while dx < dy:
            path.extend([x0 + x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 + x, y0 - y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 - y, 1.0, 1.0, 1.0])

            if d1 < 0:
                x += 1
                dx += 2 * b * b
                d1 += dx + b * b
            else:
                x += 1
                y -= 1
                dx += 2 * b * b
                dy -= 2 * a * a
                d1 += dx - dy + b * b

        d2 = b * b * (x + 0.5) * (x + 0.5) + a * a * (y - 1) * (y - 1) - a * a * b * b

        while y >= 0:
            path.extend([x0 + x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 + y, 1.0, 1.0, 1.0])
            path.extend([x0 + x, y0 - y, 1.0, 1.0, 1.0])
            path.extend([x0 - x, y0 - y, 1.0, 1.0, 1.0])

            if d2 > 0:
                y -= 1
                dy -= 2 * a * a
                d2 += a * a - dy
            else:
                y -= 1
                x += 1
                dx += 2 * b * b
                dy -= 2 * a * a
                d2 += dx - dy + a * a

    def __render(self) -> None:
        # Update all shader uniforms.
        self.pixelShader.use()
        self.pixelShader.setFloat("windowWidth", self.windowWidth)
        self.pixelShader.setFloat("windowHeight", self.windowHeight)

        # Render all shapes.
        for s in self.shapes:
            s.render()
