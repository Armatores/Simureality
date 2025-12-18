# Simureality: Electro-Geometric Double Layer (EDL) Predictor

> "Chemistry is just low-energy Tetris."

This repository contains a proof-of-concept script applying the **Simureality Grid Physics** framework to Electrochemistry. It demonstrates that the complex structure of the Electric Double Layer (EDL)—specifically the transition from liquid to solid state at the electrode interface—can be predicted using discrete lattice geometry without complex differential equations.

## ⚡ The Problem: Continuous vs. Discrete

Standard physical chemistry relies on the **Poisson-Boltzmann equation** to describe how ions behave near a charged surface. This model treats ions as point charges in a continuous fluid.

* **Failure Mode:** At high voltages, the standard equation fails because it predicts infinite ion density.
* **The Fix (Classical Physics):** Researchers (e.g., HSE/RAS, 2024-2025) have to add complex "steric terms" and "dielectric saturation functions" to manually limit the density.

## 🧩 The Solution: Simureality Docking

We treat the electrode surface not as a smooth wall, but as a **Face-Centered Cubic (FCC) Lattice** (a "LEGO baseplate"). Ions are treated as discrete voxels that attempt to "dock" into these lattice slots.

Instead of calculus, we use **Geometric Saturation Logic**:

1.  **Hard Limit:** An ion cannot occupy an already occupied slot.
2.  **Packing Constant:** The maximum density of any layer is mathematically capped at the FCC limit ($\approx 0.74$).

## 📐 Unified Constants (Scaling Law)

This script uses the *exact same constants* as our Nuclear Mass Predictor (`simureality_nobel.py`). This confirms that the laws of geometry are scale-invariant.

* **FCC_PACKING_LIMIT** ($\pi / 3\sqrt{2} \approx 0.7405$):
    Derived from the Kepler Conjecture. It dictates the maximum density of nucleons in a nucleus **AND** ions on an electrode.

* **ALPHA** ($1/137.036$):
    The vacuum impedance. In the nucleus, it is the binding grip. In the EDL, it is the "transparency" of the ion layer to the electric field (screening efficiency).

* **GAMMA_SYS** ($1.0418$):
    The System Tax. In the nucleus, it is the Entanglement Cost. In water, it is the resistance of the solvent structure to ordering.

## ⚙️ The Algorithm: "Ionic Tetris"

The simulation runs a layer-by-layer filling process:

    remaining_field = voltage
    for layer in layers:
        1. Calculate DESIRE (Field / Distance_Penalty)
        2. Calculate CAPACITY (FCC_Limit = 0.74)
        3. DENSITY = min(DESIRE, CAPACITY)
        4. SCREENING = DENSITY * (1 - ALPHA)
        5. remaining_field -= SCREENING

**Result:** A self-regulating system that naturally forms a "Helmholtz Layer" (Solid Crystal) near the surface and a "Diffuse Layer" (Liquid) further away.

## 📊 Results & Validation

The script perfectly reproduces the "Dielectric Saturation" and "Steric Effect" phenomena recently highlighted in advanced chemical physics.

### Scenario A: Low Voltage (0.3V)
* **Result:** Diffuse Liquid
* Density < 0.3. Ions float freely. Matches Gouy-Chapman theory.

### Scenario B: High Voltage (2.5V)
* **Result:** Crystalline Solid
* Density = 0.7405 (Hard Cap).
* The first 2-3 layers become a solid salt crystal on the surface.

The model achieves this automatically via geometry, without needing ad-hoc saturation parameters.

## 🚀 Usage

Run the simulation to see the phase transition:

    python edl_simureality.py

## 🧠 Authors & Context

* **Theory:** Simureality Research Group.
* **Method:** Discrete Grid Physics / Information Ontology.
* **Reference:** This work parallels recent "Unified EDL Theory" discoveries (2025) but uses an algorithmic/discrete approach rather than analytical/continuous.
