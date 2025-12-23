# Simureality V17: Multiverse Compatibility Test

## Description
This script implements the **Theory of Material Relativity** within the **Simureality** framework.

**Objective:** To prove that "material quality" is not an absolute constant but depends on the reference frame (the Core Material). The script simulates three distinct "universes" where the laws of physics remain the same, but the geometric baseline changes:

* **Universe W (Tungsten Standard):** High density ($Vol \approx 9.5$).
* **Universe Cu (Copper World):** Very high density ($Vol \approx 7.1$).
* **Universe Mg (Magnesium World):** Low density / "Fluffy" ($Vol \approx 14.0$).

The algorithm demonstrates how a material considered "trash" in one universe (e.g., Zirconium in the W-Universe) becomes a "champion" in another (Mg-Universe) due to Impedance Matching.

## Theoretical Basis
The script tests two competing factors that determine interface quality:

1. **Universal Metabolism (Absolute Factor):** Some materials are inherently better at handling entropy due to their internal structure.
    * **Plasticity Bonus:** Soft metals (Au, Ag) are universally good adapters.
    * **Noise Penalty:** Distorted lattices (Zn) are universally noisy.
    * **Decoherence Penalty:** Low-density materials (Ca, Zr) are inherently "leaky" for electron waves.

2. **Geometric Relativity (Relative Factor):** The interface quality depends on the Volume Mismatch between the Candidate and the Core.

$$Penalty = |1 - \frac{Vol_{candidate}}{Vol_{core}}|$$

A perfect match ($Penalty \to 0$) can override inherent internal defects.

## Algorithm Logic
The code iterates through three Cores (W, Cu, Mg). For each core, it recalculates the score of every candidate element:

### 1. Static Interface Score (Relative)
Calculated based on the specific core of the current universe.
* **Density Match:** How well does the candidate's atom fit the core's lattice?
* **Wetting Bonus:** Soft materials get a boost regardless of the core.

### 2. Metabolism Factor (Absolute)
Calculated based on the candidate's intrinsic properties ($c/a$ ratio, yield strength, absolute volume). This acts as a global modifier.

### 3. Final Score
`Final Score = Static Score (Relative) × Metabolism Factor (Absolute)`

## Key Predictions (What to look for)
* **The "Universal Tape" Phenomenon:** Gold (Au) and Silver (Ag) remain at the top in almost all universes due to their extreme plasticity, which compensates for geometric mismatches.
* **The Rise of Iron:** In the Copper Universe, Iron (Fe) rises to the top because its volume (7.09) is a near-perfect match for Copper (7.11). This explains the stability of Cu-Fe interfaces (e.g., copper-clad steel).
* **The Zirconium Redemption:** In the Magnesium Universe, Zirconium (Zr) — usually penalized for being "fluffy" — becomes a top-tier material because it matches Magnesium's low density perfectly. This predicts the viability of Mg-Zr alloys in aerospace.

## Requirements
* Python 3.x
* pandas
* numpy
