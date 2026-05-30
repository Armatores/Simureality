# 🌌 Grid Physics: Global Resonance Scanner (`global_scanner.py`)

**An Ab-Initio Topological Reverse-Engineering Suite for Nuclear Mass, Deformation, and Radioactive Decay.**

Part of the **Simureality (Grid Physics)** Research Initiative.

---

## 🔬 Overview

Classical nuclear physics relies on the "Liquid Drop Model," assuming the atomic nucleus is a continuous, incompressible fluid. The **Global Resonance Scanner** shatters this assumption by treating the universe as a discrete computational substrate (a Face-Centered Cubic Information Lattice).

This Streamlit-based application merges two of the largest experimental nuclear databases in the world:

1. **AME2020 (Atomic Mass Evaluation):** Used to calculate the *Topological Debt* (mass defect) of a nucleus.
2. **NUBASE2020:** Used to correlate geometric structural noise with experimental radioactive half-lives.

By processing thousands of isotopes, `global_scanner.py` mathematically decompiles nuclear mass into discrete geometric shapes, proving that **nuclear deformation is quantized** and that **radioactive decay is a deterministic Garbage Collection process** triggered by spatial misalignment (Jitter).

---

## 🔑 The Core Discovery: The "Staircase of Shape Phases"

The scanner calculates the physical length of every heavy isotope along its Z-axis using the fundamental L1-Cache lattice step of the Matrix ($\lambda_p \approx 1.3214 \text{ fm}$).

When mapping calculated nuclear length against the Mass Number ($A$), the application reveals a striking phenomenon:

* **The Continuous Model Fails:** Nuclei do not stretch smoothly (e.g., 8.1, 8.2, 8.3 layers).
* **The Discrete Staircase:** Stable nuclei strictly cluster on **integer lattice layers** (e.g., exactly 8.0, 9.0, or 11.0 layers). This is the *Attractor State* where the nuclear core perfectly resonates with the macroscopic Vacuum Gate ($3.3249 \text{ \AA}$).
* **Garbage Collection (Decay):** Isotopes that fall into fractional inter-layer spaces (e.g., 8.5 layers) generate severe computational noise (**Jitter Tax**). The Universe's operating system algorithmically flags these fractional nodes and executes a spontaneous decay protocol (Alpha/Beta/Fission) to trim the geometry back to an integer resonance.

---

## 🚀 Features & Dashboards

The application is divided into three primary analytical tabs:

1. **📊 The Deformation Staircase (Phase Transitions):** An interactive Plotly scatter plot demonstrating the quantized jumps in nuclear geometry. Visually confirms why heavy nuclei (like Lead-208) form hollow "rugby ball" spheroids precisely 9 layers long.
2. **🔥 Vacuum Noise Heatmap (Jitter Tax):**
A Segrè chart (Z vs N) colored by Topological Jitter. Green zones represent geometric harmony (Stable isotopes). Red zones highlight severe fractional misalignment, perfectly mapping the origins of radioactivity without relying on quantum probability.
3. **🗄️ System Log (Raw Reverse-Topology):**
The raw pandas dataframe exposing the exact number of broken macro-links, topological debt in MeV, and predicted geometric layers for every synthesized isotope.

## 🧮 Theoretical Background (The Hardware API)

The scanner uses zero empirical fitting coefficients (no Weizsäcker terms). It operates strictly on the immutable hardware constants of the Grid Physics framework:

* **Base Lattice Step ($\lambda_p$):** $1.3214 \text{ fm}$
* **Alpha-Cluster Payload ($E_{\alpha}$):** $28.32 \text{ MeV}$
* **Macro-Link Profit ($E_{macro\_link}$):** $2.425 \text{ MeV}$
* **Jitter Penalty ($J_{tax}$):** $0.01311 \text{ MeV}$ per unclosed I/O port.

*If an ideal greedy spherical assembly produces a mass that is "too light" compared to AME2020, the scanner identifies this as Geometry Overflow. It calculates the exact number of macroscopic bonds the Universe had to sever to stretch the nucleus into a stable, hollow resonant antenna.*

---

**License:** MIT License
**Author:** Simureality Research Group
