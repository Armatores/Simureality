# 🗑️ Simureality: GC Routing Extractor (Radioactive Decay Decompiler)

[](https://www.google.com/search?q=%23)
[](https://www.google.com/search?q=%23)
[](https://www.google.com/search?q=%23)

This module serves as a decompiler for the vacuum's **Garbage Collector (GC)**.

Within the framework of **Grid Physics** and the discrete 3D lattice theory (FCC Lattice), radioactive decay is not a "quantum randomness" or a probabilistic dice roll. Decay is a strictly deterministic exception-handling process (geometry error resolution) within the Universe's operating system.

The half-life ($T_{1/2}$) is the physical **Execution Time** of the vacuum's memory cleanup algorithm. This script extracts the hidden hardware constants of this algorithm directly from the AME2020 / NUBASE database.

## 🧠 Fundamental Architecture (The Engine)

Classical physics uses phenomenological models with dozens of fitting coefficients. We use architectural reverse engineering. The time it takes for the vacuum to remove an unstable isotope depends on three hardware network parameters:

1.  **Topological Debt ($\Delta K$):** The geometric assembly error of the nuclear crystal (in MeV). The larger the error, the higher the task priority for the GC.
2.  **Network Impedance ($Z$):** The number of protons. Protons form a dense Coulomb network. Depending on the error type, this network acts either as a "bottleneck" (Packet Loss) or as overpressure.
3.  **Hardware Lock ($P_{lock}$):** The presence of dangling/unpaired ports (Spin). Odd isotopes create dynamic Jitter, forcing the Garbage Collector to spend CPU cycles on synchronization.

## 🔀 Dual Routing Protocol

Data analysis via multiple linear regression proved that the vacuum uses two different interrupt handlers depending on the macro-crystal size:

  * **Hardware Dump (Alpha decay, $Z > 82$):** When a massive transuranic crystal is overloaded, the Garbage Collector tears off an entire Alpha-tetrahedron from it. Coulomb resistance ($Z$) acts as overpressure here — protons *help* tear the lattice from the inside (explosive decompression).
  * **Software Patch (Beta decay, $Z \le 82$):** When the crystal is small, the GC does not destroy the geometry but programmatically "reflashes" the corrupted node (isospin flip neutron $\leftrightarrow$ proton). Here, $Z$ acts as a brake: the more nodes in the nucleus, the longer the GC indexes links for safe patch application.

## 🧮 GC Routing Equation

The script automatically calculates the clock rate of the base timer ($T_{base}$) and the component weights for both protocols using the following formula:

$$\log_{10}(T_{1/2})=T_{base}+Z_{imp}\cdot Z+E_{pow}\cdot\sqrt{\Delta K}+P_{lock}\cdot Unpaired$$

*Where:*

  * $T_{base}$ — Base reset limit (Hardware timer).
  * $Z_{imp}$ — Network impedance coefficient.
  * $E_{pow}$ — Error reset power.
  * $Unpaired$ — Presence of unpaired ports (0 or 1).

## 🚀 Installation and Usage

The script is written in Python using Streamlit for visualization. It strictly avoids "black boxes" like Random Forest algorithms — relying solely on transparent linear algebra (`scikit-learn` / `numpy`) to preserve the physical meaning of every extracted constant.

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/simureality-gc-extractor.git
cd simureality-gc-extractor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```
