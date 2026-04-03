# 🧊 Simureality Phase Engine (V33.3)
**Absolute Hardware Thermodynamics via Graph Topology and Vacuum Impedance**

## Overview
This engine is a computational proof-of-concept for the **Simureality** framework. It predicts macroscopic thermodynamic phase transitions (Melting, Boiling, Pyrolysis) of various molecules without relying on empirical chemical tables, van der Waals constants, or predefined enthalpies. 

Instead, the engine treats molecules as discrete 3D informational graphs and calculates their stability strictly through **geometric topology** and acoustic friction against the **Vacuum Impedance ($Z_0 \approx 377\ \Omega$)**.

## ⚙️ Core Architecture & Physics

The Matrix does not know what "Water" or "Benzene" is. It only sees mass distribution and network ports. The engine deconstructs molecules into three hardware caches:

1. **Voxel Footprint (Labute ASA):** The raw surface area of the molecule. This acts as the baseline "volume anchor," keeping the graph in a liquid state (RAM cache) via structural drag.
2. **3D Inertia Tensors (PMI):** The engine calculates Principal Moments of Inertia to dynamically determine the shape of the graph (*Sphericity, Disk-ness, Rod-ness*). Perfect spheres (like $CCl_4$) or flat disks (like Benzene) gain massive "packing efficiency" bonuses, raising their crystallization points.
3. **True P2P Port Scanner:** The script explicitly scans for exposed topological interfaces:
    * **Donors:** Polar hydrogens.
    * **Acceptors:** Lone pairs on $O, N, F$.

### The "Topological Frustration" Concept
To form a perfect solid crystal (ROM cache), a molecule requires 100% P2P symmetry (e.g., Water: 2 donors / 2 acceptors). 
If a graph has asymmetrical ports (e.g., Ammonia with 3 donors / 1 acceptor, or Ethanol with 1 donor / 2 acceptors), the unpaired ports create **Topological Frustration**. These unpaired interfaces physically interfere with the 3D packing process, resulting in a severe mathematical penalty to the melting point ($T_{melt}$).

### The Impedance Bridge (Dimensional Calibration)
The engine calculates the graph's structural holding power in raw geometric units. To translate this abstract topology into macroscopic Temperature (Kelvin), we use the **Impedance Bridge**:

$$T = Raw\_Topology \times \left( \frac{Z_0}{100} \right) \times \gamma_{sys}$$

Where $Z_0 = 377$ (Vacuum Impedance) and $\gamma_{sys} = 1.0418$ (Simureality System Tax). The multiplier is universally applied to all molecules, successfully predicting phase transitions for both ultra-polar networks ($H_2O$) and blind inertial liquids ($C_6H_6$) using a single physical law.

## 📊 Extracted Macro-States

* 🧊 **$T_{melt}$ (Crystallization / ROM Lock):** The temperature at which structural packing and symmetric P2P handshakes overcome thermal jitter.
* 💧 **$T_{boil}$ (Boiling / RAM Cache):** The temperature at which the structural footprint and secondary network links fail, detaching the graphs into the vacuum (Gas phase).
* 🔥 **$T_{deg}$ (Pyrolysis / Kernel Panic):** The critical failure point of the primary covalent axis.

## 🚀 Installation & Usage

1. Install the required dependencies:
```bash
pip install streamlit pandas numpy plotly rdkit
```
2. Run the Streamlit application:
```bash
streamlit run phase_engine_v33.py
```
3. Use the **Single Scan** to view real-time area charts of phase transitions, or use the **Batch Process** to compile a complete dataframe of all hardcoded systems.

---

### ⚠️ Project Status: Proof of Concept (WIP)
**Notice:** This software is currently in the active development and conceptual validation stage. It is a Proof-of-Concept (PoC) designed to demonstrate the validity of the Simureality topological methodology. While the Impedance Bridge provides highly accurate predictions for a wide range of standard molecules ($H_2O, C_6H_6, NH_3$), the volumetric scaling factors (ASA multipliers) exhibit minor non-linearities for medium-mass molecules lacking P2P networks. The algorithms are subject to ongoing architectural refactoring and calibration. Do not use for industrial chemical engineering.
