# Project Simureality: Geometric Chemistry Engine (FCC Lattice)

> **"Chemistry is not a list of rules; it is the inevitable result of packing spheres into a 3D grid."**

![Status](https://img.shields.io/badge/Status-Experimental-orange) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## 🌌 Overview

This repository hosts the **Lattice Chemistry Simulator**, a computational proof-of-concept for the **Simureality Theory**.

Instead of solving complex Schrödinger wave equations to predict atomic stability, this engine treats atoms as **geometric configurations of vectors** (electrons) on a discrete **Face-Centered Cubic (FCC)** vacuum lattice.

We demonstrate that "Magic Numbers" (2, 10, 18 - Noble Gases) and chemical stability are **emergent properties of geometry**, arising naturally from the requirement to minimize geometric tension (impedance) on a grid.

---

## 📐 The Hypothesis

Standard physics views electrons as probability clouds defined by wave functions. **Simureality** posits a "Hardware-First" approach:

1.  **Space is Discrete:** The vacuum is a structured grid (likely FCC or HCP packing).
2.  **Particles are Vectors:** Electrons are fundamental units of information occupying lattice nodes.
3.  **Forces are Geometric:** Coulomb's Law is a simplified description of lattice impedance minimization.
4.  **Stability = Symmetry:** An atom is "stable" (chemically inert) when its electrons form a perfectly symmetrical geometric shape that distributes tension evenly (e.g., Tetrahedron, Octahedron).

---

## ⚙️ How It Works

The script `lattice_chemistry.py` performs the following steps:

1.  **Lattice Generation:** Creates a 3D Face-Centered Cubic (FCC) grid.
    * *Why FCC?* It represents the densest possible packing of spheres (Kepler Conjecture), minimizing empty space.
2.  **Configuration:** Places $Z$ electrons and a nucleus ($+Z$) on the grid.
3.  **Optimization:** Uses **Stochastic Hill Climbing** to find the arrangement with the lowest total energy.
4.  **Energy Calculation:**

    The objective function minimizes the total system tension $E$:

    $$E_{total} = E_{repulsion} - E_{attraction}$$

    Where:

    $$E_{repulsion} = \frac{1}{2} \sum_{i \neq j} \frac{1}{||\mathbf{r}_i - \mathbf{r}_j||}$$

    $$E_{attraction} = \sum_{i} \frac{Z}{||\mathbf{r}_i||}$$

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.8+
* NumPy
* Matplotlib

### Setup

    git clone [https://github.com/your-username/project-trilex.git](https://github.com/your-username/project-trilex.git)
    cd project-trilex
    pip install numpy matplotlib

### Running the Simulation

    python lattice_chemistry.py

The script will:
1.  Iterate through Atomic Numbers $Z=1$ to $Z=20$.
2.  Find the ground state geometry for each atom.
3.  Generate a plot `simureality_fcc_scan.png` showing stability valleys.

---

## 📊 Expected Results

The simulation consistently finds "Energy Valleys" (Stability Peaks) at specific electron counts, matching the Periodic Table without being told about quantum shells.

| Atomic Number (Z) | Element | Geometric Shape (Simureality) | Standard Physics |
| :---: | :---: | :--- | :--- |
| **2** | **Helium** | Linear / Tetrahedron (Draft) | 1s² (Full Shell) |
| **10** | **Neon** | Symmetric Polyhedron | 2p⁶ (Full Shell) |
| **18** | **Argon** | Extended Symmetric Grid | 3p⁶ (Full Shell) |

> **Note:** The "Energy per Electron" graph will show local minima at these numbers, indicating that adding one more electron (breaking the symmetry) requires a disproportionate amount of energy.

---

## 🛠 Features

* **Vectorized Calculations:** Fast NumPy operations for distance matrices.
* **Stochastic Relaxation:** "Shaking" the atom to avoid local minima.
* **Visualization:** Auto-generated plots highlighting Noble Gas configurations.
* **Grid Agnostic:** Code structure allows easy swapping of FCC for HCP or SC lattices for comparison.

---

## 🔮 Future Roadmap

- [ ] **3D Visualization:** Export atomic geometries to `.obj` or `.ply` for 3D rendering.
- [ ] **Spin Integration:** Add vector orientation (Spin Up/Down) as a constraint for the energy function ($137$ factor).
- [ ] **Proton Folding:** Simulate the nucleus not as a point charge, but as a packed geometry of quarks.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*This project is part of the **Simureality** research initiative. We build the Vector Computer.*
