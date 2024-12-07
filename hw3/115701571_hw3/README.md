# HW3

Name: Akshat Sharma

SBU ID: 115701571

Email: akshat.sharma@stonybrook.edu

## Overview

Implemented a sample program to display flat-shaded triangle, tetrahedron and sphere (with tessellation shaders).
Also implemented a FPS-style camera and local illumination with the Phong shading model.

Note: Directory `./var/` contains vertices for the required polyhedral objects.
Each line denotes a 3D point (x, y, and z coordinates), and each 3 lines denote a triangular facet.
Note that many points are duplicated as they appear in multiple facets!

## Compile & Run

```bash
conda activate py3
python main.py
```

## Features Implemented

Check all features implemented with "x" in "[x]"s.
Features or parts left unchecked here won't be graded!

-   [x] **P0: Global Functionalities** (See each object for display modes)
    -   [x] Camera Functionalities
        -   [x] Show/hide x, y, z Axes
        -   [x] `W`/`S`/`A`/`D`/`UP`/`DOWN` Functionalities
-   [x] **P1: Simple Polyhedral Objects**
    -   [x] Tetrahedron
        -   [x] Wireframe
        -   [x] Flat
        -   [x] Smooth
    -   [x] Cube
        -   [x] Wireframe
        -   [x] Flat
        -   [x] Smooth
    -   [x] Octahedron
        -   [x] Wireframe
        -   [x] Flat
        -   [x] Smooth
-   [x] **P2: Icosahedron**
    -   [x] Wireframe
    -   [x] Flat
    -   [x] Smooth
    -   [x] Subdivision
-   [x] **P3: Ellipsoid**
    -   [x] Wireframe
    -   [x] Flat
    -   [x] Smooth
    -   [x] Subdivision
-   [x] **P4: Tessellation**
    -   [x] Sphere
        -   [x] Wireframe
        -   [x] Flat/Smooth
    -   [x] Cylinder
        -   [x] Wireframe
        -   [x] Flat/Smooth
    -   [x] Cone
        -   [x] Wireframe
        -   [x] Flat/Smooth
-   [x] **P5: Torus**
    -   [x] Wireframe
    -   [x] Flat
    -   [x] Smooth
    -   [x] Subdivision
-   [x] **P6: Super-quqdrics And Dodecahedron**
    -   [x] Super-quqdrics
        -   [x] Wireframe
        -   [x] Flat/Smooth
        -   [x] Dynamically Load Parameters
    -   [x] Dodecahedron
        -   [x] Wireframe
        -   [x] Flat
        -   [x] Smooth
        -   [x] Subdivision
-   [x] **P7: Flight Simulation**
    -   [x] City Scene Assembly (Has 8-12 urban structures)
    -   [x] Display
        -   [x] Wireframe
        -   [x] Flat
        -   [x] Smooth
    -   [x] Loops
        -   [x] Horizontal Loop
        -   [x] Vertical Loop
-   [ ] **P8: Bonus**
    -   [ ] Normal Display Mode
    -   [ ] Other (Please Specify)
