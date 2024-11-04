import glm
from typing import Tuple, List, Optional
import os


class SplineIO:
    @staticmethod
    def save_spline(filepath: str, control_points: List[glm.vec2], is_c2: bool) -> bool:
        """
        Save spline control points to a configuration file.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "w") as f:
                # Write header: 2D/3D flag, C2/C1 flag, number of points
                f.write(f"2 {2 if is_c2 else 1} {len(control_points)}\n")

                # Write control points
                for point in control_points:
                    f.write(f"{point.x} {point.y}\n")

            return True

        except Exception as e:
            print(f"Error saving spline: {e}")
            return False

    @staticmethod
    def load_spline(
        filepath: str,
    ) -> Tuple[Optional[List[glm.vec2]], Optional[bool], Optional[bool]]:
        """
        Load spline control points from a configuration file.
        """
        try:
            control_points = []

            with open(filepath, "r") as f:
                # Read and parse header
                dim_flag, continuity_flag, num_points = map(
                    int, f.readline().strip().split()
                )

                is_2d = dim_flag == 2
                is_c2 = continuity_flag == 2

                # Read control points
                for _ in range(num_points):
                    x, y = map(float, f.readline().strip().split())
                    control_points.append(glm.vec2(x, y))

            return control_points, is_2d, is_c2

        except Exception as e:
            print(f"Error loading spline: {e}")
            return None, None, None
