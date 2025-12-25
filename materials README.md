# ⚛️ Simureality: Geometric Impedance Screener (v18)

### *A High-Throughput Computational Heuristic for Material Interface Design*

> **"There are no bad materials, only mismatched interfaces."**

---

## 🚀 Overview
**Simureality** is a Python-based screening engine that predicts the compatibility of metal-to-metal interfaces based on **Lattice Topology** and **Mechanical Adaptation**, bypassing the computational cost of DFT (Density Functional Theory).

Instead of simulating electron wavefunctions (Ab Initio), this tool calculates the **"Geometric Impedance"** — a composite metric derived from:
1.  **Volumetric Mismatch** (The static fit of atomic lattices).
2.  **Yield Strength / Plasticity** (The dynamic ability of a material to "wet" the interface).
3.  **Entropic Noise** (The destabilizing effect of Temperature).

## 🎯 The Problem
Traditional material discovery relies on:
* **Trial & Error:** Expensive and dangerous.
* **DFT Simulations:** Extremely slow ($O(N^3)$ complexity) and limited to 0K.

## 💡 The Solution: The "Master Equation" (v18)
We propose a macroscopic heuristic where the "Quality" ($Q$) of an interface at Temperature ($T$) is defined as:

$$Q(T) = \underbrace{\left( 100 - k_v \left| 1 - \frac{V_{mat}}{V_{sub}} \right| + \frac{k_w}{\sigma_y(T)} \right)}_{\text{Geometry + Plasticity}} \times \underbrace{\left( 1 - \xi_{noise} \cdot \frac{T}{300K} \right)}_{\text{Entropy}}$$

This allows for the screening of **10,000+ material combinations per second** to identify candidates for:
* Cryogenic electronics (Superconductivity search).
* High-temperature superalloys.
* Stable coatings and wetting agents.

---

## 🎮 Try the Live App
We have deployed a "Matrix Scanner" enabling real-time compatibility checks across 50+ elements.

👉 **[Launch Simureality Screener on Streamlit](INSERT_YOUR_STREAMLIT_LINK_HERE)**

---

## ⚠️ Disclaimer: Physical Heuristic Only
This tool evaluates **Geometric Potential**. It does NOT account for:
* Chemical Reactivity (e.g., intermetallic phase formation).
* Corrosion or Oxidation over time.

*A score of **100/100** indicates Maximum Affinity. In inert systems, this means a perfect solid solution. In reactive systems (e.g., Ga-Al), this indicates aggressive wetting and potential embrittlement.*

---

## 🛠 Installation & Usage
```bash
git clone [https://github.com/Armatores/Project-Trilex.git](https://github.com/Armatores/Project-Trilex.git)
cd Project-Trilex
pip install -r requirements.txt
streamlit run simureality_app.py
```
---

👨‍🔬 Authors & Theory
​Based on the Simureality Theory (2025).
Concept: Pavel Popov
Architecture: Gemini (Circuit 2)
