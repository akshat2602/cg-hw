from OpenGL.GL import *
import glm
import copy
from .glshape import GLShape
from .renderable import Renderable
from util import Shader
from .bezier_curve import BezierCurve


class C2Spline(GLShape, Renderable):
    def __init__(self, shader: Shader):
        super().__init__(shader)
        self.interpolation_points = []
        self.control_points = []
        self.segments = []
        self.selected_node_index = -1
        self.preview_point = None

    def update_preview(self, preview_point: glm.dvec2):
        self.preview_point = glm.vec2(preview_point.x, preview_point.y)

    def get_preview_segments(self) -> list[BezierCurve]:
        if not self.preview_point or len(self.interpolation_points) < 2:
            return []

        temp_points = copy.deepcopy(self.interpolation_points)
        temp_points.append(self.preview_point)

        preview_control_points = []

        preview_control_points.extend(self.control_points)

        if len(temp_points) >= 3:
            last_3_points = temp_points[-3:]
            preview_control_points.append(temp_points[-1])
            preview_control_points.extend(
                self._add_derived_control_points(last_3_points)
            )

        preview_segments = []
        if len(preview_control_points) >= 4:
            i = 0
            while i < len(preview_control_points) - 3:
                segment = BezierCurve(self.shader, preview_control_points[i : i + 4])
                preview_segments.append(segment)
                i += 3

        return preview_segments

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

        # Update position of selected node
        self.control_points[self.selected_node_index] = glm.vec2(new_pos.x, new_pos.y)

        # Skip updates if moving endpoint
        if self._is_endpoint(self.selected_node_index):
            self._update_segments()
            return

        # Update control points based on node type
        if self._is_interpolation_point(self.selected_node_index):
            self._propagate_changes_forward(self.selected_node_index)
        else:
            self._propagate_changes_bidirectional(self.selected_node_index)

        self._update_segments()

    def _is_endpoint(self, index: int) -> bool:
        return index == 0 or index == len(self.control_points) - 1

    def _is_interpolation_point(self, index: int) -> bool:
        return index % 3 == 0

    def _propagate_changes_forward(self, start_idx: int):
        for i in range(start_idx + 1, len(self.control_points) - 1):
            if i % 3 == 1:
                self._update_first_control_point(i)
            elif i % 3 == 2:
                self._update_second_control_point(i)

    def _propagate_changes_backward(self, start_idx: int):
        segment = (start_idx // 3) - 1
        segment_start = segment * 3

        for i in range(segment_start, 0, -1):
            if i % 3 == 2:
                self._update_prev_second_control_point(i)
            elif i % 3 == 1:
                self._update_prev_first_control_point(i)

    def _propagate_changes_bidirectional(self, middle_idx: int):
        curr_segment = middle_idx // 3
        next_segment_start = (curr_segment + 1) * 3
        curr_segment_start = curr_segment * 3

        # Update forward
        for i in range(next_segment_start, len(self.control_points) - 1):
            if i % 3 == 1:
                self._update_first_control_point(i)
            elif i % 3 == 2:
                self._update_second_control_point(i)

        # Update backward
        for i in range(curr_segment_start, 0, -1):
            if i % 3 == 2:
                self._update_prev_second_control_point(i)
            elif i % 3 == 1:
                self._update_prev_first_control_point(i)

    def _update_first_control_point(self, idx: int):
        p1 = self.control_points[idx - 1]  # Previous point
        p0 = self.control_points[idx - 2]  # Two points back

        self.control_points[idx] = glm.vec2(2.0 * p1.x - p0.x, 2.0 * p1.y - p0.y)

    def _update_second_control_point(self, idx: int):
        p0 = self.control_points[idx - 4]  # First point of previous segment
        p1 = self.control_points[idx - 3]  # Second point of previous segment
        p2 = self.control_points[idx - 1]  # First point of current segment

        self.control_points[idx] = glm.vec2(
            p0.x + 2.0 * (p2.x - p1.x), p0.y + 2.0 * (p2.y - p1.y)
        )

    def _update_prev_first_control_point(self, idx: int):
        p0 = self.control_points[idx + 4]  # Last point of next segment
        p1 = self.control_points[idx + 3]  # Second-to-last point of next segment
        p2 = self.control_points[idx + 1]  # First point of current segment

        self.control_points[idx] = glm.vec2(
            p0.x + 2.0 * (p2.x - p1.x), p0.y + 2.0 * (p2.y - p1.y)
        )

    def _update_prev_second_control_point(self, idx: int):
        p1 = self.control_points[idx + 1]  # Next point
        p2 = self.control_points[idx + 2]  # Two points ahead

        self.control_points[idx] = glm.vec2(2.0 * p1.x - p2.x, 2.0 * p1.y - p2.y)

    def _update_control_points(self):
        self.control_points.append(self.interpolation_points[-1])
        last_3_points = self.interpolation_points[-3:]
        self.control_points.extend(self._add_derived_control_points(last_3_points))

    def _add_derived_control_points(
        self, last_3_points: list[glm.vec2]
    ) -> list[glm.vec2]:
        p0, p1, p2 = last_3_points
        p3 = glm.vec2(x=(2 * p2.x) - p1.x, y=(2 * p2.y) - p1.y)
        p4 = glm.vec2(x=p0.x + 2 * (p3.x - p2.x), y=p0.y + 2 * (p3.y - p2.y))
        return [p3, p4]

    def _update_segments(self):
        if len(self.control_points) < 4:
            return

        self.segments = []
        i = 0
        while i < len(self.control_points):
            segment = BezierCurve(self.shader, self.control_points[i : i + 4])
            self.segments.append(segment)
            i += 3

    def delete_selected_node(self) -> bool:
        if self.selected_node_index == -1:
            return False

        # Don't delete endpoints
        if (
            self.selected_node_index == 0
            or self.selected_node_index == len(self.control_points) - 1
        ):
            return False

        # Clear all points if 4 or fewer points remain
        if len(self.control_points) <= 4:
            self.control_points.clear()
            self.segments.clear()
            self.selected_node_index = -1
            return True

        num_segments = (len(self.control_points) - 1) // 3
        deleted_segment = self.selected_node_index // 3

        # Store original length for bounds checking
        original_length = len(self.control_points)

        # Handle interpolation points (every third point)
        if self.selected_node_index % 3 == 0:
            if self.selected_node_index == 0:  # First point
                # Remove first three points
                self.control_points = self.control_points[3:]
                self._propagate_changes_forward_delete(0)

            elif self.selected_node_index == original_length - 1:  # Last point
                # Remove last three points
                self.control_points = self.control_points[:-3]
                if len(self.control_points) > 0:
                    self._propagate_changes_backward_delete(
                        len(self.control_points) - 1
                    )

            else:  # Middle interpolation point
                # Remove point and surrounding control points
                self.control_points = (
                    self.control_points[: self.selected_node_index - 2]
                    + self.control_points[self.selected_node_index + 3 :]
                )
                # Update both directions if we have enough points
                if len(self.control_points) > self.selected_node_index:
                    self._propagate_changes_forward_delete(self.selected_node_index)
                if self.selected_node_index > 0:
                    self._propagate_changes_backward_delete(self.selected_node_index)

        # Handle control points
        else:
            if deleted_segment == num_segments:  # Last segment
                # Remove last three points
                self.control_points = self.control_points[:-3]
                if len(self.control_points) > 0:
                    self._propagate_changes_backward_delete(
                        len(self.control_points) - 1
                    )
            else:
                # Remove point and two following points
                self.control_points = (
                    self.control_points[: self.selected_node_index]
                    + self.control_points[self.selected_node_index + 3 :]
                )
                if len(self.control_points) > self.selected_node_index:
                    self._propagate_changes_forward_delete(self.selected_node_index)

        self.selected_node_index = -1
        self._update_segments()
        return True

    def _propagate_changes_forward_delete(self, start_idx: int):
        """Updates control points forward after deletion."""
        for i in range(start_idx + 1, len(self.control_points) - 1):
            if i % 3 == 1:
                # Same as movement but with different point references
                p1 = self.control_points[i - 1]
                p0 = self.control_points[i - 2]
                self.control_points[i] = glm.vec2(2.0 * p1.x - p0.x, 2.0 * p1.y - p0.y)
            elif i % 3 == 2:
                # Different point references for deletion
                # Note: After deletion, the indices shift
                p0 = self.control_points[i - 4]
                p1 = self.control_points[i - 3]
                p2 = self.control_points[i - 1]
                self.control_points[i] = glm.vec2(
                    p0.x + 2.0 * (p2.x - p1.x), p0.y + 2.0 * (p2.y - p1.y)
                )

    def _propagate_changes_backward_delete(self, start_idx: int):
        # Only propagate if we have enough points to work with
        remaining_points = len(self.control_points)
        if remaining_points < 3:
            return

        for i in range(min(start_idx - 1, remaining_points - 1), 0, -1):
            # Ensure we have enough points ahead for the calculations
            if i % 3 == 2 and i + 2 < remaining_points:
                # Handle second control point
                p1 = self.control_points[i + 1]
                p2 = self.control_points[i + 2]
                self.control_points[i] = glm.vec2(2.0 * p1.x - p2.x, 2.0 * p1.y - p2.y)

            elif i % 3 == 1 and i + 4 < remaining_points:
                # Handle first control point
                p0 = self.control_points[i + 4]
                p1 = self.control_points[i + 3]
                p2 = self.control_points[i + 1]
                self.control_points[i] = glm.vec2(
                    p0.x + 2.0 * (p2.x - p1.x), p0.y + 2.0 * (p2.y - p1.y)
                )

    def add_interpolation_point(self, point: glm.dvec2, last_point: bool = False):
        point_vec2 = glm.vec2(point.x, point.y)

        if len(self.interpolation_points) < 3 or last_point:
            self.interpolation_points.append(point_vec2)
            self.control_points = copy.deepcopy(self.interpolation_points)
            if last_point:
                self.preview_point = None
        else:
            self.interpolation_points.append(point_vec2)
            self._update_control_points()
            self.interpolation_points = copy.deepcopy(self.control_points)

        self._update_segments()
        return self.control_points

    def render(self, timeElapsedSinceLastFrame: int, animate: bool) -> None:
        # Render individual segments
        for segment in self.segments:
            segment.render(timeElapsedSinceLastFrame, animate)

        preview_segments = self.get_preview_segments()
        for segment in preview_segments:
            segment.render(timeElapsedSinceLastFrame, animate)
