# EC 425 Quiz 2 — Phong Shading with Ray Tracing

**Student:** Solanki Kuldipkumar Kishorbhai  
**Roll no.:** 202351136  
**Course:** EC 425 — Computer Graphics and Multimedia

Ray tracer for a scene with **3 spheres**, a checkered ground plane, and **1 point light**. Implements Phong ambient / diffuse / specular shading, shadow rays, and iterative reflections.

## Repository layout

```
EC425_Quiz2_Phong_RayTracer/
├── src/
│   ├── raytracer_phong.cpp   # SDL3 + OpenGL 3.3 GPU ray tracer
│   └── render_outputs.py     # CPU renderer used for report screenshots
├── outputs/
│   ├── output_phong.png
│   ├── output_reflections.png
│   └── output_alt_view.png
├── docs/
│   └── EC425_Quiz2_Solanki_Kuldip.pdf
└── README.md
```

## Features

- Primary camera rays through each pixel
- Ray–sphere and ray–plane intersection (nearest hit)
- Phong lighting + shadow rays
- Iterative mirror bounces (max depth 4)
- Interactive camera orbit (drag) and light animation (Space toggles)

## Scene

| Object | Notes |
|--------|--------|
| Sphere 1 | Crimson, glossy |
| Sphere 2 | Chrome / high reflectivity |
| Sphere 3 | Brass / metallic |
| Ground | `y = -1` checkered plane |
| Light | Single orbiting point light |

## GPU build (optional)

Needs **SDL3**, **OpenGL 3.3**, and **GLAD** on your machine.

```bash
# example (adjust include/lib paths for your install)
g++ -std=c++17 src/raytracer_phong.cpp glad.c \
    -I/path/to/glad/include -I/path/to/SDL3/include \
    -lSDL3 -ldl -lGL -o raytracer_phong
./raytracer_phong
```

Controls: drag to orbit, `Space` pause animation, `Esc` quit.

## CPU screenshots (report figures)

```bash
pip install numpy pillow
python3 src/render_outputs.py
# writes PNGs into ./outputs (script uses its own output folder next to the script parent)
```

To regenerate report images from the repo root, run:

```bash
cd src && python3 render_outputs.py
# then copy PNGs from ../quiz2 path or edit OUT_DIR in the script if needed
```

The PNGs already checked into `outputs/` are the ones used in the quiz PDF.

## Report

See [`docs/EC425_Quiz2_Solanki_Kuldip.pdf`](docs/EC425_Quiz2_Solanki_Kuldip.pdf).
