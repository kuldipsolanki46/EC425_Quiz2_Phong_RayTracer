#!/usr/bin/env python3
"""EC425 Quiz 2 — CPU Phong ray tracer for report screenshots."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
W, H = 720, 480
EPS = 1e-3
INF = 1e20


@dataclass
class Ball:
    center: np.ndarray
    radius: float
    albedo: np.ndarray
    ka: float
    kd: float
    ks: float
    shininess: float
    kr: float


def norm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def reflect(i: np.ndarray, n: np.ndarray) -> np.ndarray:
    return i - 2.0 * np.dot(i, n) * n


def hit_sphere(origin, direction, ball: Ball):
    oc = origin - ball.center
    b = float(np.dot(oc, direction))
    c = float(np.dot(oc, oc) - ball.radius * ball.radius)
    disc = b * b - c
    if disc <= 0.0:
        return None
    sd = math.sqrt(disc)
    t = -b - sd
    if t <= EPS:
        t = -b + sd
    if t <= EPS:
        return None
    return t


def hit_ground(origin, direction, y_plane=-1.0):
    if abs(direction[1]) < 1e-8:
        return None
    t = (y_plane - origin[1]) / direction[1]
    if t <= EPS:
        return None
    return t


def cast_scene(origin, direction, balls):
    best_t = INF
    hit = None  # dict

    tg = hit_ground(origin, direction)
    if tg is not None and tg < best_t:
        best_t = tg
        p = origin + tg * direction
        cell = np.floor(p[[0, 2]] * 0.8)
        dark = ((cell[0] + cell[1]) % 2) == 0
        albedo = np.array([0.15, 0.16, 0.18]) if dark else np.array([0.82, 0.82, 0.86])
        hit = {
            "t": tg,
            "p": p,
            "n": np.array([0.0, 1.0, 0.0]),
            "albedo": albedo,
            "ka": 0.25,
            "kd": 0.7,
            "ks": 0.35,
            "shininess": 28.0,
            "kr": 0.22,
        }

    for ball in balls:
        t = hit_sphere(origin, direction, ball)
        if t is not None and t < best_t:
            best_t = t
            p = origin + t * direction
            hit = {
                "t": t,
                "p": p,
                "n": norm(p - ball.center),
                "albedo": ball.albedo,
                "ka": ball.ka,
                "kd": ball.kd,
                "ks": ball.ks,
                "shininess": ball.shininess,
                "kr": ball.kr,
            }
    return hit


def occluded(point, light_dir, light_dist, balls):
    origin = point + light_dir * 0.003
    for ball in balls:
        t = hit_sphere(origin, light_dir, ball)
        if t is not None and t < light_dist:
            return True
    return False


def sky_color(direction):
    t = np.clip(direction[1] * 0.5 + 0.5, 0.0, 1.0)
    return (1.0 - t) * np.array([0.10, 0.12, 0.18]) + t * np.array([0.40, 0.55, 0.78])


def phong(hit, view_dir, light_pos, light_col, amb_col, balls, shadows=True):
    ambient = hit["ka"] * amb_col * hit["albedo"]
    to_l = light_pos - hit["p"]
    dist_l = float(np.linalg.norm(to_l))
    L = to_l / dist_l
    diffuse = np.zeros(3)
    specular = np.zeros(3)
    if not (shadows and occluded(hit["p"], L, dist_l, balls)):
        ndl = max(float(np.dot(hit["n"], L)), 0.0)
        diffuse = hit["kd"] * ndl * light_col * hit["albedo"]
        R = reflect(-L, hit["n"])
        rdv = max(float(np.dot(R, view_dir)), 0.0)
        specular = hit["ks"] * (rdv ** hit["shininess"]) * light_col
    return ambient + diffuse + specular


def make_primary(u, v, eye, look_at, fov_y_deg, aspect):
    f = norm(look_at - eye)
    r = norm(np.cross(f, np.array([0.0, 1.0, 0.0])))
    up = np.cross(r, f)
    th = math.tan(math.radians(fov_y_deg) * 0.5)
    sx = (2.0 * u - 1.0) * aspect
    sy = 1.0 - 2.0 * v
    d = norm(f + sx * r * th + sy * up * th)
    return d


def render(balls, eye, look_at, light_pos, max_bounce, enable_reflections, shadows=True):
    light_col = np.array([1.0, 0.97, 0.92])
    amb_col = np.array([0.08, 0.09, 0.12])
    aspect = W / H
    img = np.zeros((H, W, 3), dtype=np.float64)

    for j in range(H):
        v = (j + 0.5) / H
        for i in range(W):
            u = (i + 0.5) / W
            direction = make_primary(u, v, eye, look_at, 50.0, aspect)
            origin = eye.copy()
            color = np.zeros(3)
            weight = np.ones(3)

            for bounce in range(max_bounce if enable_reflections else 1):
                hit = cast_scene(origin, direction, balls)
                if hit is None:
                    color += weight * sky_color(direction)
                    break

                view_dir = -direction
                local = phong(hit, view_dir, light_pos, light_col, amb_col, balls, shadows)
                kr = hit["kr"] if enable_reflections else 0.0
                color += weight * (1.0 - kr) * local

                if not enable_reflections or kr < 1e-4:
                    break
                weight *= kr * (0.55 * np.ones(3) + 0.45 * hit["albedo"])
                if float(np.max(weight)) < 0.012:
                    break
                origin = hit["p"] + hit["n"] * 0.003
                direction = reflect(direction, hit["n"])

            img[j, i] = color
        if (j + 1) % 80 == 0:
            print(f"  row {j+1}/{H}")

    img = np.clip(img, 0.0, None)
    img = np.power(img, 1.0 / 2.2)
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img


def scene_balls():
    # Three spheres: crimson, chrome, brass
    return [
        Ball(np.array([-1.7, 0.0, 0.3]), 1.0, np.array([0.88, 0.10, 0.14]), 0.2, 0.7, 0.75, 56.0, 0.32),
        Ball(np.array([0.5, 0.05, -0.4]), 1.1, np.array([0.92, 0.93, 0.96]), 0.15, 0.35, 1.0, 140.0, 0.80),
        Ball(np.array([2.2, -0.05, 0.6]), 0.9, np.array([0.90, 0.72, 0.20]), 0.18, 0.55, 0.85, 72.0, 0.58),
    ]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    balls = scene_balls()
    eye = np.array([3.8, 2.6, 5.4])
    look_at = np.array([0.0, 0.15, 0.0])
    light = np.array([3.5, 5.0, 2.5])

    print("Rendering Phong (no reflections)...")
    phong_img = render(balls, eye, look_at, light, max_bounce=1, enable_reflections=False)
    p1 = OUT_DIR / "output_phong.png"
    Image.fromarray(phong_img).save(p1)
    print(f"Saved {p1}")

    print("Rendering Phong + iterative reflections...")
    refl_img = render(balls, eye, look_at, light, max_bounce=4, enable_reflections=True)
    p2 = OUT_DIR / "output_reflections.png"
    Image.fromarray(refl_img).save(p2)
    print(f"Saved {p2}")

    # Alternate camera for a third useful figure
    print("Rendering alternate camera view...")
    eye2 = np.array([-4.2, 2.2, 4.8])
    alt = render(balls, eye2, look_at, light, max_bounce=4, enable_reflections=True)
    p3 = OUT_DIR / "output_alt_view.png"
    Image.fromarray(alt).save(p3)
    print(f"Saved {p3}")


if __name__ == "__main__":
    main()
