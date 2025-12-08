# Simureality: The Geometric Origins of Electron Orbitals

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Geometric_Proof-orange.svg)]()

> **"Chemistry is not the interaction of abstract probability clouds. It is the distinct addressing of nodes on a discrete 3D lattice."**

## 🧪 Overview

This repository contains the computational proofs for the **Simureality Chemistry Model**. 

Standard Quantum Mechanics describes electron orbitals ($s, p, d, f$) as complex probability density functions derived from the Schrödinger equation. We propose a radical simplification: **Orbitals are simply address vectors pointing to the nearest neighbors on a Face-Centered Cubic (FCC) lattice.**

This repository contains two distinct scripts that prove this hypothesis from opposite directions:
1.  **Generative Proof:** Simulates electrons self-organizing on a grid to find stability (Spontaneous Shell Formation).
2.  **Analytic Proof:** Scans standard Quantum Mechanical orbitals to prove they align perfectly with integer lattice coordinates.

---

## 📂 The Scripts

| Script File | Type | Description |
| :--- | :--- | :--- |
| `lattice_shell_solver.py` | **Generative** | Simulates point charges on an FCC grid. Spontaneously derives the Periodic Table's magic numbers (2, 10, 18). |
| `orbital_vector_scanner.py` | **Analytic** | Analyzes standard spherical harmonics ($Y_{lm}$) and proves their maximum density vectors point to discrete grid nodes. |

---

## 🚀 1. The Generative Proof (`lattice_shell_solver.py`)

**The Question:** If we place electrons on a discrete grid and tell them only to "minimize repulsion" (Coulomb law), what shapes will they form?

**The Logic:**
* **No Quantum Mechanics:** The script knows nothing about wave functions or Pauli exclusion.
* **The Grid:** It uses a discrete Face-Centered Cubic (FCC) lattice as the only allowed position space.
* **The Algorithm:** It adds electrons one by one ($Z=1$ to $20$) and uses a stochastic hill-climbing algorithm to find the lowest energy configuration.

### 📉 The Result (Interpretation)
The simulation outputs an energy stability graph that reveals distinct "kinks" (stability peaks) at specific numbers. These are not random; they are geometric closures:

* **Z = 2 (Helium):** Stability is found at a linear configuration (opposite poles). **Geometry: Line.**
* **Z = 10 (Neon):** A massive stability jump occurs when 8 electrons form a perfect cube around the center. **Geometry: Cube.**
* **Z = 18 (Argon):** The next stability plateau occurs when the faces/edges of the cube are filled. **Geometry: Octahedron/Cuboctahedron.**

**Conclusion:** The structure of the Periodic Table is an inevitable consequence of packing repelling spheres onto a cubic lattice.

---

## 🧭 2. The Analytic Proof (`orbital_vector_scanner.py`)

**The Question:** Do the "mysterious" shapes of quantum orbitals ($p_x, d_{xy}, f_{xyz}$) align with our proposed lattice?

**The Logic:**
* The script takes the standard mathematical formulas for electron orbitals (Spherical Harmonics).
* It scans 3D space to find the vector where the electron probability is **maximum**.
* It checks if these vectors correspond to integer coordinates on an FCC grid.

### 📊 The Result (Interpretation)
The script confirms a 100% match between Quantum Orbitals and Lattice Geometry:

| Orbital Type | Max Vector | Lattice Interpretation |
| :--- | :--- | :--- |
| **s-orbital** | `[0,0,0]` | **The Node** (Sphere center) |
| **p-orbitals** | `[1,0,0]` | **The Faces** (6 neighbors in a cube) |
| **d-orbitals** | `[1,1,0]` | **The Edges** (12 diagonal edge centers) |
| **f-orbitals** | `[1,1,1]` | **The Corners** (8 tetrahedral voids) |

**Conclusion:** Electron orbitals are not "clouds." They are **Address Busses**.
* Chemistry is simply the activation of specific ports (Face, Edge, or Corner) on the voxel interface.

---

## 🛠️ Installation & Usage

No heavy scientific libraries are required beyond `numpy` and `matplotlib`.

```bash
# Clone the repository
git clone [https://github.com/your-username/simureality-chemistry.git](https://github.com/your-username/simureality-chemistry.git)

# Run the Generative Solver (Produces Stability Graph)
python lattice_shell_solver.py

# Run the Vector Scanner (Produces Text Report)
python orbital_vector_scanner.pyTheoretical Implication

​By combining these two scripts, we demonstrate a unified truth:
​Bottom-Up: Electrons naturally form cubes and lines when placed on a lattice (Script 1).
​Top-Down: Standard Quantum Mechanics describes exactly these lattice directions (Script 2).
​Therefore, Wave-Particle Duality is an illusion caused by the discrete nature of the vacuum. We perceive "waves" only because we are observing the activation of discrete lattice addresses over time.
​Part of the Simureality Project. 2025.

