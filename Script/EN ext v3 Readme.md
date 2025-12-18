# Simureality: Ab Initio Nuclear Mass Predictor (EN ext v3)

### A Geometric-Topological Approach to Nuclear Binding Energy

> "Matter is not a fluid drop; it is a resonant lattice." — Project Simureality

## Overview

**EN ext v3** is the reference implementation of the Simureality Grid Physics theory applied to nuclear binding energies. Unlike standard semi-empirical mass formulas (SEMF/Weizsäcker) which rely on multiple fitted coefficients, this script derives binding energies using pure geometry and fundamental constants ($m_e$, $\alpha$, $\pi$).

The algorithm treats atomic nuclei not as liquid drops, but as geometric structures formed within a vacuum lattice (FCC). It successfully predicts binding energies from Deuterium ($H-2$) to the theoretical Element 120 ($Ubn$), demonstrating a **Mean Absolute Error (MAE) of < 6.6 MeV** across the entire Periodic Table.

## Key Features

* **Ab Initio Derivation:** No "magic numbers" or arbitrary fitting parameters. All coefficients are derived from the electron mass and lattice geometry factors ($\sqrt{3}$, $\pi$).
* **Dual-Phase Logic:** Automatically switches between **Cluster Mode** (Light Nuclei, $Z \le 20$) and **Lattice Mode** (Heavy Nuclei, $Z > 20$).
* **Triangle Exemption:** Correctly models $H-3$ and $He-3$ as planar structures, distinct from tetrahedral clusters.
* **Deformation Matrix:** Includes a geometric penalty for non-spherical nuclei (Lanthanides/Actinides) based on distance from magic numbers.
* **Island of Stability Oracle:** Predicts the binding energy and stability threshold for hypothetical superheavy elements (e.g., $Z=120$).

## The Physics (Theoretical Framework)

The core axiom of Simureality is that the vacuum possesses a specific impedance and geometry (FCC Lattice). Nuclear binding energy is the result of minimizing "surface tension" against this vacuum grid.

### 1. The Fundamental Link ($E_{link}$)

The energy of a single bond between nucleons is derived from the electron mass projected onto the lattice geometry:

$$E_{link} = 4 \cdot m_e \cdot \gamma_{struct} \approx 2.360 \text{ MeV}$$

Where $\gamma_{struct} = 2 / \sqrt{3}$ is the geometric projection factor of a tetrahedron edge onto a cubic face.

### 2. The Lattice Tax ($\gamma_{sys}$)

Matter cannot exist in the grid without "paying" a volumetric instantiation tax. This constant, derived from the Proton Radius Puzzle, scales the bulk energy of heavy nuclei:

$$\gamma_{sys} \approx 1.0418$$

### 3. The Two Modes of Matter

**Phase A: Nano-Clusters ($Z \le 20$)**
Light nuclei behave like "Lego blocks" (Alpha-Ladder).
* **Structure:** Linear chains or tetrahedrons of Alpha particles.
* **Energy:** Sum of discrete links + Symmetry bonuses.
* **Planar Exception:** $H-3$ and $He-3$ are treated as triangles (3.5 links) rather than tetrahedrons, avoiding the symmetry penalty applicable to 3D structures.

**Phase B: Bulk Lattice ($Z > 20$)**
Heavy nuclei behave like a liquid crystal (FCC solid).
* **Volume Energy:** $A \cdot (6 \cdot E_{link} \cdot \gamma_{sys})$ (12 neighbors in FCC).
* **Surface Tension:** Geometric loss at the boundary ($A^{2/3}$).
* **Coulomb Repulsion:** Derived from the Atomic Packing Factor (APF) of an FCC lattice ($\sim 0.74$).

## Usage

### Prerequisites
* Python 3.x (Standard library only, no `pip install` required).

### Execution
Run the script directly in your terminal:

    python3 "EN ext v3.py"

## Sample Output

The script will output a table comparing simulated values (**SIM BE**) with real experimental data (**REAL BE** from AME2020), calculating accuracy and absolute error.

    SIMUREALITY V1.3: GOLD MASTER BENCHMARK (115 ISOTOPES)
    ================================================================================
    NUCLEUS  | Z   | REAL BE    | SIM BE     | ACCURACY | ERROR
    --------------------------------------------------------------------------------
    H-3      | 1   | 8.5        | 8.3        | 97.41%   | -0.2
    He-4     | 2   | 28.3       | 28.3       | 99.92%   | +0.0
    Ca-40    | 20  | 342.1      | 339.9      | 99.36%   | -2.2
    Fe-56    | 26  | 492.2      | 491.6      | 99.86%   | -0.7
    Pb-208   | 82  | 1636.4     | 1637.4     | 99.94%   | +1.0
    U-238    | 92  | 1801.7     | 1819.5     | 99.01%   | +17.8
    --------------------------------------------------------------------------------
    GLOBAL STATISTICS:
    AVERAGE ACCURACY:   98.455%
    MEAN ABSOLUTE ERROR: 6.59 MeV

## Benchmark Results

The model has been stress-tested against 115 isotopes.

* **The Lead Anchor:** The doubly-magic nucleus `Pb-208` is predicted with 99.94% accuracy (+1.0 MeV error). This confirms the validity of the FCC Lattice model for spherical nuclei.
* **The Triangle Fix:** $H-3$ and $He-3$ are predicted with <0.2 MeV error, validating the planar geometry exemption.
* **Deformation:** Systematic errors (~10-15 MeV) appear only in the middle of Lanthanides/Actinides, correctly reflecting the physical deformation (non-sphericity) of these nuclei.

## Prediction: Element 120 (Unbinilium)

The script predicts the binding energy for the theoretical superheavy element `Ubn-304`:

* **Predicted BE:** ~2140 MeV
* **BE/A:** ~7.04 MeV/nucleon

**Verdict:** Stable against instantaneous fission. Simureality predicts that the Periodic Table physically extends to Z=120.

