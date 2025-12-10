# Simureality Nucleosynthesis: Ab Initio Derivation of Nuclear Binding Energies

## 1. Overview
This repository contains the source code and validation data for the **Simureality Nucleosynthesis Model**. 

Unlike standard nuclear physics models (e.g., Liquid Drop Model), which rely on semi-empirical constants, this project demonstrates that nuclear binding energies can be derived **ab initio** from discrete geometry. We postulate that physical reality operates on a **Face-Centered Cubic (FCC) Lattice**, and fundamental forces are geometric constraints of this topology.

**Key Axiom:** The binding energy of an atomic nucleus is the sum of its geometric components ("Bricks" and "Links") on the lattice.

## 2. Methodology: Deriving Constants from Scratch

We use **zero** empirical nuclear data to calibrate the model. All constants are derived from the mass of the electron and geometric projection factors.

### A. The Fundamental Unit
* **Electron Mass ($m_e$):** `0.511 MeV` (Base Unit)

### B. Geometric Projection (The System Tax)
Mapping a tetrahedral structure (Alpha particle) onto a cubic grid introduces a lattice tension factor $\gamma$, defined by the ratio of a triangle's side to its height:
$$\gamma = \frac{2}{\sqrt{3}} \approx 1.1547$$

### C. Derived Interaction Energies
1.  **Lattice Link ($E_{link}$):** Corresponds to a single geometric edge (Up-quark string, $N=2$ nodes).
    $$E_{link} = 4 \cdot m_e \cdot \gamma \approx \mathbf{2.360 \text{ MeV}}$$

2.  **Alpha Brick ($E_{\alpha}$):** A single cubic voxel frame consists of 12 edges.
    $$E_{\alpha} = 12 \cdot E_{link} \approx \mathbf{28.322 \text{ MeV}}$$
    *(Compare to experimental He-4 energy: 28.30 MeV. Accuracy: 99.92%)*

## 3. The Alpha-Ladder Algorithm

For alpha-conjugate nuclei ($N=Z$, mass $A=4n$), the nucleus is modeled as a crystalline cluster of $n$ tetrahedrons.
The number of internal links ($L$) is governed by the rigidity topology formula:
$$L = 3n - 6 \quad (\text{for } n \ge 3)$$

**Prediction Formula:**
$$E_{binding} = (n \cdot E_{\alpha}) + (L \cdot E_{link})$$

## 4. Results (Validation against CODATA)

The following table compares the Simureality Geometric Prediction against experimental data (CODATA/AME2020).

| Nucleus | Structure | Links | Geometric Pred. (MeV) | Real Energy (MeV) | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **He-4** | Unit | 0 | 28.32 | 28.30 | **99.92%** |
| **Be-8** | Dimer | 0 | 56.64 | 56.50 | **99.74%** |
| **C-12** | Triangle | 3 | 92.05 | 92.16 | **99.88%** |
| **O-16** | Tetrahedron | 6 | 127.45 | 127.62 | **99.87%** |
| **Ne-20** | Bi-pyramid | 9 | 162.85 | 160.64 | **98.62%** |
| **Mg-24** | Octahedron | 12 | 198.26 | 198.25 | **99.99%** |
| **Si-28** | Stack | 15 | 233.66 | 236.53 | **98.79%** |
| **S-32** | Dual-Tetra | 18 | 269.06 | 271.78 | **99.00%** |
| **Ar-36** | Crystal | 21 | 304.47 | 306.72 | **99.27%** |
| **Ca-40** | Closed Core | 24 | 339.87 | 342.05 | **99.36%** |

**Average Accuracy:** 99.44%

## 5. Interpretation

1.  **Effective Geometry:** The incredibly high accuracy (peaking at 99.996% for Magnesium-24) confirms that for symmetric matter, the "Effective Binding Energy" is purely additive. The geometric tension factor $\gamma$ accounts for the intrinsic resistance of the vacuum.
2.  **The Calcium Limit:** The model holds up to Calcium-40. Beyond this point, the "Hidden Cost" of Coulomb repulsion (which grows as $Z^2$) exceeds the structural capacity of the lattice, requiring the introduction of neutron excess ($N > Z$) to stabilize the structure.

## 6. Usage

Run the main simulation script:
```bash
python simureality_nucleosynthesis.py
