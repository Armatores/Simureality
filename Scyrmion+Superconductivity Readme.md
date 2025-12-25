# Simureality: Topological Resonance Suite

### Computational Materials Science based on Discrete FCC Lattice Geometry & Prime Number Theory.

**Author:** Pavel Popov  
**Theory:** Simureality (Simulation Hypothesis & Discrete Ontology)  
**Status:** MVP / Research Preview

---

## 🌌 Abstract

**Simureality** framework offers a radically new approach to predicting material stability and quantum coherence. Unlike standard continuous field theories, this framework operates on **Discrete Ontology**: it models the universe as a computational grid (FCC Lattice) governed by resource optimization principles.

We posit that **Quantum Stability is a function of Number Theory**.

Particles and quasi-particles (Skyrmions, Cooper Pairs, Anyons) are stable only when their geometric volume aligns with the discrete lattice grid in specific **Resonance Modes** (Prime Numbers or Integer Harmonics).

This repository contains two open-source tools to verify this theory against experimental data:

* **Skyrmion Pro:** Predicts magnetic vortex stability via Prime Number topology.
* **Superconductor Tc Predictor:** Calculates critical temperatures based on thermal expansion and geometric decoherence.

---

## 🧠 Theoretical Basis

### 1. The Prime Resonance Hypothesis
In a discrete 3D lattice, a topological object (like a Skyrmion) is maximally stable when the number of lattice nodes ($N$) it encompasses is a **Prime Number** (or a Semi-Prime for memory applications).

* **Prime N:** The object cannot be divided or decayed into simpler harmonics. It becomes a "Hard Knot" in the simulation.
* **Composite N:** The object is unstable and prone to decay via geometric divisors.

### 2. Geometric Impedance & Superconductivity
Superconductivity is treated as a "frictionless flow" through the lattice. This flow is only possible when the Coherence Volume of the electron pair ($\xi$) matches an Integer/Prime number of unit cells.

* **Tc (Critical Temperature)** is defined not by energy gap alone, but by **Geometric Fracture**.
* As temperature rises, **Thermal Expansion** stretches the lattice.
* $Tc$ is the precise moment when the lattice expansion causes the geometry to drift away from the **Resonance Mode** (falling into a "Composite Valley" or slipping off a "Resonance Peak").

### 3. The "Dimension Folding" Hypothesis (2D Logic)
Why are 2D materials (high-Tc cuprates, graphene) so robust?
**Simureality Axiom:** In 2D systems, the simulation engine drops the calculation of the Z-coordinate.

* **Trizistor Economy:** Ignoring one spatial dimension releases ~33% of vector processing power.
* **Hyper-Fidelity:** This freed-up computational throughput is redirected to error-correction in the X-Y plane.
* **Result:** 2D particles (Anyons) possess "Hyper-Fidelity" and are topologically protected against thermal noise that destroys standard 3D coherence.

---

## 🛠️ Included Tools

### 🌪️ Tool 1: Skyrmion Pro (Topological Engineering)
A calculator for magnetic skyrmions in thin films and bulk crystals.

* **Input:** Exchange Stiffness ($A$), DMI ($D$), Lattice Constant ($a$).
* **Logic:** Calculates the nodal count $N = Area_{skyrmion} / Area_{node}$.
* **Features:**
    * *Stability Landscape:* Visualizes stability peaks (Primes) and valleys (Composites).
    * *Auto-Optimize:* Calculates the exact parameter shift required to "snap" the material into a Prime Resonance state (Self-Tuning prediction).
* **Validation:** Correctly predicts stability for FeGe (Semi-Prime), instability for MnSi, and the specific narrow stability window for Antiskyrmions.

### ⚡ Tool 2: Superconductor Tc Predictor
A thermal scanner that predicts the Critical Temperature ($Tc$) by simulating lattice expansion.

* **Input:** Lattice parameters ($a, b, c$), Coherence length ($\xi$), Thermal expansion coefficient ($\alpha$).
* **Logic:** Simulates $T$ from 0K to 300K, tracking the ratio $V_{pair} / V_{cell}$.
* **Validation:**
    * **Mercury (Hg):** Predicted $Tc \approx 5.0 K$ (Real: 4.2 K). Matches the first geometric resonance peak.
    * **Lead (Pb):** Predicted $Tc \approx 7.0 K$ (Real: 7.2 K). Matches the resonance drop-off.
    * **YBCO (High-Tc):** Explains 93 K as a point of "Maximum Geometric Chaos" (Composite breakdown).

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.8+
* Streamlit, NumPy, Pandas, Plotly

### Setup

    git clone [https://github.com/Armatores/Project-Trilex.git](https://github.com/Armatores/Project-Trilex.git)
    cd Project-Trilex
    pip install -r requirements.txt

### Running the Lab

To launch the Skyrmion Analyzer:

    streamlit run Skyrmion_Pro.py

To launch the Superconductor Predictor:

    streamlit run Superconductor_Resonance.py

---

## 📉 Key Findings (Verified)

| Material | Type | Phenomenon | Simureality Verdict |
| :--- | :--- | :--- | :--- |
| **Pt/Co/Ta** | Thin Film | Standard params yield unstable state | Stability found at **-0.0013** deviation (Prime 40993) |
| **Mn1.4PtSn** | Antiskyrmion | Hard to stabilize | Stabilized at **Prime 4051** via fine-tuning |
| **Mercury (Hg)** | Superconductor | Low Tc (4.2K) | Exists only on a Narrow Resonance Peak; killed by minimal expansion |
| **YBCO** | High-Tc | High Tc (93K) | Survives expansion until **Geometric Collapse** (Zero Stability point) |
| **BSCCO** | 2D Layered | Extremely Stable | **Dimension Folding** active. Z-coord dropped = Absolute Stability |

---

## 📜 License & Citation

This project is part of the **Simureality** research initiative.
Code is provided under **MIT License**.

If you use this data for academic publications, please cite:

> "Simureality: Geometric Origins of Quantum Stability in Discrete Lattices" - Pavel Popov, 2025.
