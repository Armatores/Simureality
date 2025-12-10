# Graphene Resonance Scanner: Geometric Prediction of Magic Angles

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![Physics](https://img.shields.io/badge/Physics-Condensed%20Matter-blue) ![Theory](https://img.shields.io/badge/Theory-Lattice%20Resonance-purple)

### Ab Initio Derivation of Twistronic Anomalies via Vacuum Impedance Coupling

## 1. Overview

This repository contains a computational tool for predicting "Magic Angles" in Twisted Bilayer Graphene (TBG).

Unlike standard Band Theory approaches (which require complex Hamiltonian diagonalization), this model treats the phenomenon as a **Geometric Resonance** between the Moiré superlattice and the fundamental impedance of the vacuum.

**Key Discovery:** We demonstrate that superconductivity and topological states emerge when the number of atoms ($N$) in the Moiré supercell aligns with a **Half-Integer Harmonic** of the Inverse Fine Structure Constant ($\alpha^{-1} \approx 137.036$).

---

## 2. Theoretical Basis

The Simureality/Grid Physics framework postulates that physical vacuum possesses a discrete geometric impedance. For a signal (electron current) to propagate without resistance (superconductivity), the material's lattice geometry must synchronize with the vacuum's "bus width."

### The Resonance Equation
Since electrons are fermions (Spin $1/2$), the resonance condition requires a **Half-Integer** phase lock:

$$
N_{atoms} \approx (k + \frac{1}{2}) \cdot \alpha^{-1}
$$

Where:
* $N_{atoms}$: Number of Carbon atoms in one Moiré supercell.
* $\alpha^{-1}$: The vacuum impedance constant ($137.035999...$).
* $k$: An integer harmonic index.

### Geometric Derivation
For a hexagonal lattice with twist angle $\theta$ defined by commensurate index $i$:

$$
N = 4 \cdot (3i^2 + 3i + 1)
$$

$$
\cos(\theta) = \frac{3i^2 + 3i + 0.5}{3i^2 + 3i + 1}
$$

---

## 3. Key Findings & Validation

The script scans the angular spectrum and identifies peaks where the lattice geometry matches the resonance condition with $<0.05\%$ error.

| Harmonic ($k.5$) | Angle ($\theta$) | Precision | Physical Significance |
| :--- | :--- | :--- | :--- |
| **40.5** | **1.54°** | **99.98%** | **Experimental Baseline.** Used as a reference point in *Nature* (2023) [1]. |
| **61.5** | **1.25°** | **99.99%** | **Topological State.** Region of Chern insulators and emerging flatness. |
| **81.5** | **1.08°** | **99.96%** | **The Magic Angle.** The precise theoretical peak for superconductivity. |
| **92.5** | **1.02°** | **99.99%** | **Fine Structure.** Often cited as the lower bound of the magic range. |

### The "Smoking Gun": 1.54°
The angle **1.54°** is often used in high-precision simulations (e.g., *npj 2D Materials and Applications* [1]) as a stable test case. Our model blindly identifies this angle as the **40.5-harmonic** resonance, explaining its stability.

---

## 4. Usage

The tool is a standalone Python script requiring no external libraries beyond `math`.

### Installation

```bash
git clone [https://github.com/YourRepo/Graphene-Scanner.git](https://github.com/YourRepo/Graphene-Scanner.git)
cd Graphene-Scanner
```

### Running the Scan

```bash
python graphene_resonance.py
```

### Sample Output

```text
INDEX  | ANGLE (deg)  | ATOMS (N)    | RATIO (N/137)   | DEV FROM X.5
...
21     | 1.5385       | 5548         | 40.4857         | 0.0143 << FERMIONIC SYNC
26     | 1.2482       | 8428         | 61.5021         | 0.0021 << FERMIONIC SYNC
30     | 1.0845       | 11164        | 81.4676         | 0.0324 << FERMIONIC SYNC
...
```

---

## 5. Interpretation of Results

* **Integer Ratios ($k.0$):** Characteristic of Bosonic systems. Not expected for electron transport.
* **Half-Integer Ratios ($k.5$):** Characteristic of **Fermionic systems**. These peaks correspond to maximal electronic correlation and superconductivity.
* **Deviation:** Lower deviation = Cleaner resonance. The peak at **1.25°** (Dev 0.0021) suggests a highly ordered, though perhaps insulating, state (Topological Lock).

## 6. References

1.  *Effect of Coulomb impurities on the electronic structure of magic angle twisted bilayer graphene*, npj 2D Materials and Applications (2023). [Link](https://www.nature.com/articles/s41699-023-00403-2)
2.  *Grid Physics: A Geometric Unification*, Simureality Research Group (2025).

---
*License: MIT*
