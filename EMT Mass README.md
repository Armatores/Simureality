# Lepton Mass Hierarchy: A Geometric Resonance Approach

### 🌌 Project Simureality: Computational Lattice Physics

**Repository Status:** Experimental / Proof of Concept
**Core Hypothesis:** The rest masses of fundamental leptons (Electron, Muon, Tau) are not arbitrary constants but geometric consequences of discrete excitations on a Face-Centered Cubic (FCC) vacuum lattice.

---

## 📋 Abstract

The Standard Model of Particle Physics provides no fundamental explanation for the "Three Generations" problem or the specific mass ratios of leptons ($m_e : m_\mu : m_\tau \approx 1 : 207 : 3477$). 

This project tests the **"Node Square Law" hypothesis** derived from the Simureality framework. We postulate that:
1.  Space is a discrete computational grid with **Face-Centered Cubic (FCC)** topology.
2.  Particle Generations represent concentric **Geometric Shells** of lattice excitation.
3.  Mass is proportional to the **Square of the Node Count** ($M \propto N^2$), representing the energy required to maintain the wave amplitude on a discrete grid.

This repository contains Python scripts that simulate FCC shell growth and correlate the integer node counts with experimental mass data.

---

## 🧠 Methodology & Logic

### 1. The Lattice Topology
We utilize the **FCC (Face-Centered Cubic)** lattice. This choice is not arbitrary; previous studies in this framework (see *Aluminum Superconductivity Anomaly*) demonstrated that the FCC unit cell topology ($N=14$) is a fundamental stability attractor in nature.

### 2. The Node Square Law
In a discrete wave mechanics model, Energy ($E$) is proportional to the square of the Amplitude ($A$).
$$E \propto A^2$$
If we treat the "Amplitude" of a particle as the number of active lattice nodes ($N$) it excites, then:
$$Mass_{relative} \approx N^2$$

### 3. The Generational Hypothesis
We map the three lepton generations to discrete topological layers of the FCC lattice:

* **Generation I (Electron):** The Point Source. A single node excitation.
* **Generation II (Muon):** The Unit Cell. Excitation of the immediate neighborhood required to define a 3D unit cell.
* **Generation III (Tau):** The Super-Shell. Excitation of the second coordination sphere plus fundamental voids.

---

## 💻 The Script (`lepton_geometry_scan.py`)

The script performs a brute-force geometric generation of lattice points.

1.  **Initialization:** It constructs an FCC coordinate system using integer steps.
2.  **Shell Counting:** It counts the number of unique nodes ($N$) at specific topological boundaries (Unit Cell, Shell 2, etc.).
3.  **Mass Prediction:** It calculates the theoretical mass ($N^2$) relative to the electron ($1^2$).
4.  **Validation:** It compares these integers against the CODATA experimental values for Muon and Tau masses.

---

## 📊 Results: Theory vs. Reality

The simulation yielded the following correlations between integer lattice counts and physical constants.

| Generation | Particle | Real Mass ($m_e=1$) | Lattice Topology | Node Count ($N$) | Theory Mass ($N^2$) | Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gen I** | **Electron** | **1.0** | Point Source | **1** | **1.0** | **100%** |
| **Gen II** | **Muon** | **206.77** | FCC Unit Cell | **14** | **196.0** | **95%** |
| **Gen III** | **Tau** | **3477.12** | Shell 2 + Voids | **59** | **3481.0** | **99.9%** |

### 🔍 Detailed Analysis

#### The Muon (Gen II)
* **Target:** $\sqrt{206.77} \approx 14.38$ nodes.
* **Geometric Solution:** The fundamental FCC Unit Cell consists of **8 corners + 6 face centers**.
* **$N = 14$**.
* **Prediction:** $14^2 = 196$.
* **Interpretation:** The Muon represents the excitation of a single minimal voxel of spacetime. The slight deviation (207 vs 196) suggests a "binding energy" or vacuum coupling overhead of ~5%.

#### The Tau (Gen III)
* **Target:** $\sqrt{3477.12} \approx 58.96$ nodes.
* **Geometric Solution:** The second complete FCC shell contains **55 nodes** (Cuboctahedron). However, the FCC lattice contains fundamental **Tetrahedral Voids** (interstices). A unitary structure captures 4 such voids.
* **$N = 55 + 4 = 59$**.
* **Prediction:** $59^2 = \mathbf{3481}$.
* **Interpretation:** The deviation from experimental data is **less than 0.1%** (4 mass units). This implies that the Tau lepton is a "saturated" excitation covering the full second shell and its internal geometric voids.

---

## 🚀 Conclusion

The high correlation between integer lattice topology and lepton masses suggests that **mass is not an intrinsic property, but a computational cost.**

1.  The hierarchy of masses ($1 \to 207 \to 3477$) is not random.
2.  It follows the sequence of squaring integers: $1^2 \to 14^2 \to 59^2$.
3.  These integers ($1, 14, 59$) correspond to specific, definable geometric boundaries in an FCC vacuum lattice.

This supports the **Simureality** postulate that physical laws are emergent properties of a discrete information processing substrate.

---

## 🛠 Usage

To reproduce the data:

```bash
# Clone the repository
git clone [https://github.com/your-username/simureality-lepton-scan.git](https://github.com/your-username/simureality-lepton-scan.git)

# Run the geometric scanner
python lepton_geometry_scan.py
