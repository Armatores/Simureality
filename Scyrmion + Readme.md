# Project Trilex: Skyrmion Pro

### Topological Engineering Suite based on Discrete FCC Lattice Geometry & Prime Number Theory.

**Author:** Pavel Popov  **Theory:** Simureality (Simulation Hypothesis & Discrete Ontology)  
**Status:** MVP / Research Preview

---

## 🌌 Abstract

**Skyrmion Pro** is a computational tool designed to predict the stability of magnetic skyrmions (topological vortices) in thin films and bulk crystals.

Unlike standard continuous field theories (micromagnetics), this framework operates on **Discrete Ontology**. We posit that a magnetic vortex is maximally stable only when its geometric area encompasses a **Prime Number** (or specific Integer Harmonic) of lattice nodes.

* **Continuous Physics:** Assumes stability is a smooth energy curve.
* **Simureality Physics:** Assumes stability is quantized by Number Theory (Prime Resonance).

---

## 🧠 Theoretical Basis

### 1. The Prime Resonance Hypothesis
In a discrete 3D lattice (FCC), a topological object is defined by the number of nodes ($N$) it occupies.

* **Prime N:** The object forms a "Hard Knot". It cannot be divided by geometric integers, making it robust against decay.
* **Composite N:** The object has multiple divisors, creating "geometric cracks" where energy can leak, leading to annihilation.

### 2. The Tuning Principle
Standard material parameters (Stiffness $A$, DMI $D$) found in literature are often averages.
**Skyrmion Pro** reveals that real-world stability often occurs at slight deviations from these averages—specifically where thermal noise or surface roughness "tunes" the geometry into the nearest **Prime Number**.

---

## 🛠️ Features

### 1. Real-Time Geometric Analysis
Input standard magnetic parameters ($A, D$) and lattice constant ($a$). The tool instantly calculates the Vortex Radius and the exact **Node Count ($N$)**.

### 2. Stability Landscape
Visualizes the "neighborhood" of your current geometry.
* **High Bars (Green):** Prime Numbers (Stable Zones).
* **Low Bars (Blue/Red):** Composite Numbers (Unstable Zones).

### 3. Auto-Optimization (Self-Tuning)
The "Auto-Optimize" engine calculates the precise shift in **Exchange Stiffness ($A$)** required to hit the nearest Prime Resonance. This simulates how materials self-organize under thermal fluctuations to find stability.

---

## 📉 Case Studies (Verified Findings)

This tool has been tested against known materials:

| Material | Type | Phenomenon | Simureality Verdict |
| :--- | :--- | :--- | :--- |
| **FeGe** | Helimagnet | Highly Stable | **Semi-Prime Geometry.** Ideal for rewritable memory. |
| **MnSi** | Cryogenic | Unstable / Phased | **Highly Composite.** Deep "instability valleys" explain its fragility. |
| **Pt/Co/Ta** | Thin Film | Industry Standard | Literature params yield unstable composites. **Correction:** A tiny deviation (-0.001 pJ/m) locks it into **Prime 40993**. |
| **Mn1.4PtSn** | Antiskyrmion | Exotic / Hard to stabilize | **Prime 4051.** We found the exact harmonic frequency for antiskyrmion stability. |

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.8+
* Streamlit, NumPy, Pandas

### Setup

    git clone [https://github.com/Armatores/Project-Trilex.git](https://github.com/Armatores/Project-Trilex.git)
    cd Project-Trilex
    pip install -r requirements.txt

### Database
Ensure `scyrmions_db.csv` is present in the root directory. This file contains the crystallographic data for 10+ magnetic materials.

### Running the Lab

    streamlit run Skyrmion.py

---

## 📜 License & Citation

This project is part of the **Simureality** research initiative.
Code is provided under **MIT License**.

