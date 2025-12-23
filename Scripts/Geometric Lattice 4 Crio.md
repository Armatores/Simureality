# Simureality V18: Cryogenic Protocol (300K vs 4K)

## Description
This script implements the **Cryogenic Stress Test** within the **Simureality** framework, effectively simulating the **Third Law of Thermodynamics (Nernst Theorem)** applied to material interfaces.

**Objective:** To analyze how the "quality" of a material interface changes when the system is cooled from Room Temperature (300K) to near-Absolute Zero (4K).

The simulation tests the hypothesis that **Entropy Metabolism** is a dynamic function of temperature. As thermal energy is removed, the "Entropy Tax" (noise) vanishes, potentially allowing geometrically imperfect materials (like Lead or Niobium) to achieve perfect quantum coherence (Superconductivity), overriding their structural flaws.

## Theoretical Basis
* **The Death of Noise:** At 300K, atomic lattice vibrations (phonons) amplify geometric distortions. At 4K, these vibrations cease. Materials with distorted lattices (like Zinc) should perform better in the cold.
* **The Phase Shift (God Mode):** Certain materials possess a critical temperature ($T_c$). Below this threshold, a phase transition occurs (**Superconductivity**). In Simureality terms, this is a state where Internal Entropy drops to Zero, and the material achieves infinite coherence, ignoring geometric mismatches.
* **The Freezing of Plasticity:** The "Wetting Bonus" provided by soft metals (like Gold) relies on atomic mobility. At 4K, materials "freeze," slightly reducing their ability to physically adapt to the interface.

## Algorithm Logic
The script runs two scenarios for each element: **Warm (300K)** and **Cryo (4K)**.

### Dynamic Factors
* **Thermal Noise Scaling:** The penalty for lattice distortion ($c/a$ mismatch) scales with temperature ($T / 300$). In the cold, the penalty is minimized.
* **Plasticity Freeze:** The bonus for soft materials ($Yield$) is reduced by 50% at cryogenic temperatures to simulate lattice hardening.
* **Superconductivity Check:**
  If $T_{simulation} < T_{critical}$ (Material specific), the score overrides to **999.0 (GOD MODE)**.
  This simulates the Cooper Pair formation where resistance and entropy vanish.

### Static Factors (Invariant)
* **Density Mismatch:** "Fluffiness" (Low density) is a vacuum property and does not improve with cold. A hole is a hole, even at 0K.

## Key Predictions
* **Lead (Pb) & Niobium (Nb):** While mediocre at room temperature due to density/geometry issues, they enter **GOD MODE** at 4K due to superconductivity ($T_c > 4K$).
* **Zinc (Zn):** Shows **Improved** performance. It is not a superconductor at 4K ($T_c \approx 0.85K$), but the cold suppresses its inherent lattice noise.
* **Gold (Au):** Remains **Stable**. It relies on plasticity, not superconductivity. It effectively "maxed out" its stats at room temperature.

## Requirements
* Python 3.x
* pandas
* numpy
