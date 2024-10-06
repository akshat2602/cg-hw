# HW1

Name: Akshat Sharma

SBU ID: 115701571

Email: akshat.sharma@stonybrook.edu

## Overview

- Implemented a sample modern OpenGL program with GLFW as the windowing toolkit. 
- Implemented a naive Bresenham line drawing routine without edge-case handling. 


## Compile & Run
```bash
conda activate py3
python main.py
```

## Features Implemented

Check all features implemented with "x" in "[ ]"s. 
Features or parts left unchecked here won't be graded! 

- [x] 1. Line Segment (Fully Implemented in This Template)
  - [x] 0 <= m <= 1
- [x] 2. Line Segment
  - [x] Slope m < -1
  - [x] -1 <= m < 0
  - [x] 1 < m
  - [x] Vertical
- [x] 3. Ploy-line & Polygon
  - [x] Poly-line
  - [x] Polygon
- [x] 4. Circle & Ellipse
  - [x] Circle
  - [x] Ellipse
- [ ] 5. Polynomial Curve (BONUS PART-1)
  - [ ] Line
  - [ ] Quadratic Curve
  - [ ] Cubic Curve
- [x] 6. Scan-conversion (BONUS PART-2)
  - [x] Triangle
  - [x] Convex Polygon
  - [x] Concave Polygon
  - [x] Self-intersection detection & report

## Usage

- If you have implemented extra functionalities not mentioned in the manual,
  you may specify them here.
- If your program failed to obey the required mouse/keyboard gestures,
  you may also specify your own setting here.
  In this case, penalties may apply.

## FAQ: Runtime error "shader file not successfully read"

If you are using CLion or PyCharm, you should set up the working directory of the project.
First click the "hw1 | Debug" (for CLion) or "main" (for PyCharm) icon in the top-right corner, 
next click "Edit Configurations...", 
then set up the "Working directory" item to the root of your project, 
i.e., the path to `cpp/` or `py/`
(these directories should be further renamed to `yoursbuid_hwx` as specified above). 
Note that the working directory must be **exactly** root of your project 
(its parent directories, e.g. path to `hw1/`, won't work). 

## Appendix

Please include any other stuff you would like to mention in this section.
E.g., your suggestion on possible combinations of cubic curve parameters in this programming part. 
