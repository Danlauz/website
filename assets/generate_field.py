#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les champs géostatistiques d'arrière-plan du site (field-blue.png,
field-lassonde.png) par simulation spectrale FFT-MA, avec une légère
asymétrie de rang (non-gaussien, dans l'esprit de NG-FFTMA).

Dépendances : numpy, matplotlib, pillow
    pip install numpy matplotlib pillow

Usage :
    python assets/generate_field.py
Ajustez SEED, les portées (ax, ay), l'angle (theta) ou les palettes ci-dessous.
"""

import numpy as np
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

OUT   = Path(__file__).resolve().parent     # dossier assets/
SEED  = 7
NY, NX = 1000, 1600                          # hauteur, largeur (pixels)
AX, AY = 240, 95                             # portées (anisotropie)
THETA  = np.deg2rad(27)                       # rotation -> structures diagonales
SKEW   = 0.30                                 # asymétrie de rang (0 = gaussien pur)


def simulate():
    rng = np.random.default_rng(SEED)
    yy, xx = np.meshgrid(np.fft.fftfreq(NY) * NY,
                         np.fft.fftfreq(NX) * NX, indexing="ij")
    xr =  xx * np.cos(THETA) + yy * np.sin(THETA)
    yr = -xx * np.sin(THETA) + yy * np.cos(THETA)
    h  = np.sqrt((xr / AX) ** 2 + (yr / AY) ** 2)
    C  = np.exp(-(h ** 2) * 3.0)                       # covariance gaussienne
    amp = np.sqrt(np.maximum(np.fft.fft2(C).real, 0))  # racine du spectre
    Z  = rng.standard_normal((NY, NX))                 # bruit blanc
    f  = np.fft.ifft2(amp * np.fft.fft2(Z)).real       # champ gaussien (FFT-MA)
    f  = (f - f.mean()) / f.std()
    f  = f + SKEW * (f ** 2 - 1) / np.sqrt(2.0)         # asymétrie de rang
    f  = (f - f.mean()) / f.std()
    lo, hi = np.percentile(f, 1.5), np.percentile(f, 98.5)
    return np.clip((f - lo) / (hi - lo), 0, 1)


def save(field, cmap, name):
    rgb = (cmap(field)[..., :3] * 255).astype(np.uint8)
    Image.fromarray(rgb).save(OUT / name, optimize=True)
    print("écrit:", name)


if __name__ == "__main__":
    field = simulate()
    save(field, LinearSegmentedColormap.from_list(
        "lassonde", ["#0a3f6b", "#009fe3", "#5fa314", "#f39200", "#e03127"]),
        "field-lassonde.png")
    save(field, LinearSegmentedColormap.from_list(
        "ice", ["#ffffff", "#e3eef8", "#a9cae8", "#5b97cf", "#0067a6", "#0a2d4a"]),
        "field-blue.png")
    print("Terminé.")
