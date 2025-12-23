# Simureality: Geometric Lattice Impedance Model (v1.0)

**An ab-initio approach to predicting Electronic Work Functions ($\Phi$) using Discrete Grid Geometry and Solid State Mechanics.**

---

## 🔬 Abstract

This repository contains the Python implementation of the **Geometric Lattice Impedance Model**. Unlike traditional Density Functional Theory (DFT) which requires massive computational resources, this model predicts the electronic properties of metals using fundamental geometric projections derived from **Face-Centered Cubic (FCC)** topology.

The core discovery of this project is the **Quantum-Mechanical Bridge**: a direct mathematical link between a material's macroscopic mechanical stability (**Yield Strength**) and its microscopic quantum binding energy (**Work Function**).

---

## 📉 The Discovery Arc: From "Error" to "Physics"

The development of this model followed a strict data-driven evolution.

### Phase 1: The "Pure Geometry" Hypothesis
Initially, we hypothesized that the Work Function is simply the Ionization Energy ($I$) projected onto the lattice diagonal:
$$\Phi_{ideal} = I \times P_{geo}$$

**Result:**
* **Success:** Worked perfectly for rigid transition metals like **Tungsten (W)** and **Iron (Fe)** (Error < 1%).
* **Failure:** Failed significantly for soft metals. **Gold (Au)** showed an anomaly of **11.7%**. **Calcium (Ca)** failed by **31%**.

### Phase 2: The Insight
We analyzed the "errors" and discovered they were not random. The deviation from the geometric ideal correlated linearly with the **inverse of the Yield Strength** ($1/\sigma_y$).

* **Hypothesis:** A "soft" lattice cannot sustain the ideal geometric standing wave. Energy leaks via lattice instability (plasticity).
* **Validation:** By introducing a **Plasticity Tax** based on handbook Yield Strength values, the "anomaly" in Gold disappeared.

### Phase 3: The Synthesis (v1.0)
The final model integrates three physical regimes:
1.  **Rigid Regime:** Hard metals (W, Zr, Fe) follow pure geometry.
2.  **Plastic Regime:** Soft metals (Au, Ag, Ca) pay a "Plasticity Tax."
3.  **Protected Regime:** Metals with a **Pilling-Bedworth Ratio > 1** (Al, Ga) are "armored" by their oxide topology, boosting their work function.

---

## ⚙️ The Algorithm

The script `Simureality_Geometric_Impedance_v1.0.py` calculates the Work Function ($\Phi$) using the following logic:

### 1. Geometric Base
$$\Phi_{base} = I \times P_{geo}$$
Where $P_{geo}$ is the geometric projection factor ($1/\sqrt{3} \approx 0.577$ for BCC, $1/\phi \approx 0.618$ for FCC).

### 2. Plasticity Correction (The Gold Solution)
For metals with low mechanical strength, the lattice "leaks" energy:
$$\text{Loss}_{plast} \approx \frac{K}{\text{Yield Strength (MPa)}}$$
*This correction reduces the error for **Gold** from 11.7% to 1.7%.*

### 3. Topological Penalty (The Zinc Solution)
HCP (Hexagonal) lattices conflict with the cubic (FCC) vacuum topology.
* **If Yield > 190 MPa (e.g., Titanium):** The metal forces its topology on the vacuum. No penalty.
* **If Yield < 190 MPa (e.g., Zinc):** The vacuum imposes a "mismatch tax" (~15%).

### 4. Oxide Armor (The Aluminum Solution)
Metals with a **Pilling-Bedworth Ratio > 1** (Al, Ga) form a compressive oxide shell. This creates a "System Tax" confinement, boosting the energy barrier.

---

## 📊 Key Results

The model was tested on a dataset of **38 solid elements**.

| Element | Structure | Mechanics | Old Error (Pure Geo) | **New Error (v1.0)** | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tungsten (W)** | BCC | Rigid | 0.3% | **0.6%** | Pure Geometry Valid |
| **Iron (Fe)** | BCC | Rigid | 1.4% | **0.4%** | Pure Geometry Valid |
| **Zirconium (Zr)** | HCP | Rigid | 1.2% | **0.2%** | Topology Threshold Valid |
| **Gold (Au)** | FCC | **Soft** | **11.7%** | **1.7%** | **Plasticity Link Confirmed** |
| **Calcium (Ca)** | FCC | **Soft** | 31.6% | **5.3%** | Plasticity Link Confirmed |
| **Aluminum (Al)** | FCC | **P-B > 1** | 13.5% | **2.2%** | Oxide Armor Confirmed |

**Global Average Error:** ~6.5%

---

## ⚠️ Limitations & Boundary Conditions

To ensure scientific rigor, we explicitly state where the model applies:
1.  **Solid State Only:** Quasi-liquids (Cs, Rb, Ga near melting point) are excluded or show higher errors, as lattice geometry degrades.
2.  **Post-Transition Metals:** Elements like Lead (Pb) and Cadmium (Cd) show errors of ~18%. This indicates the onset of covalent bonding character, which deviates from the pure metallic lattice model.

---

## 🚀 Usage

### Prerequisites
* Python 3.x
* Pandas (`pip install pandas`)
* NumPy (`pip install numpy`)

### Running the Scan

    python Simureality_Geometric_Impedance_v1.0.py

The script will output a tabular report classifying each element by its physical regime (Pure, Yield-Corrected, or Topo-Corrected).

---

## 📜 Citation

If you use this code or methodology, please cite:
> **Popov, P. (2025).** *Geometric Lattice Impedance: Scaling Laws of Nuclear Binding Energy and Electronic Work Functions.* Simureality Research Group.

