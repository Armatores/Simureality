# The Grand Materials Leaderboard

## Description
This script is a software implementation of the **Entropy Metabolism Theory** within the **Simureality** project framework.

**Objective:** To perform a dynamic stress test on various elements to determine their suitability as an ideal interface (junction) for a rigid core material, specifically Tungsten (W).

Unlike classical DFT methods that focus solely on electronic structure, this algorithm evaluates thermodynamic and geometric compatibility. It answers the question: *"How effectively can a material transmit information and metabolize external entropy (noise) without destroying the interface structure?"*

## Theoretical Basis
The script is based on two fundamental Simureality principles:

1. **Geometric Impedance (Static Interface):** Materials must match in Molar Volume (packing density). If the "bricks" are of different sizes, the interface becomes incoherent.
2. **Entropy Metabolism (Dynamic Factor):** A material is a process, not a static object.
    * **Dissipation (Au, Ag):** High-plasticity materials "metabolize" entropy, converting mechanical stress into heat (phonons) while maintaining contact.
    * **Noise (Zn, Cd):** Materials with distorted lattices generate internal noise, degrading signal quality.
    * **Decoherence (Ca, Mg):** Low-density ("fluffy") materials lose wave coherence at the boundary.

## Algorithm Logic
The material evaluation (`Final_Score`) is calculated in two stages:

### Stage 1: Static Interface (Static Score)
Evaluates how well the candidate material fits the Tungsten Core (W).

* **Density Match:** Compares the Molar Volume of the candidate against the core (Vol W = 9.53). The larger the difference, the higher the penalty. This acts as an acoustic impedance check.
* **Wetting Bonus:** Derived from the Yield Strength. Soft metals (e.g., Au, Yield=20) receive a bonus as they act as a "liquid gasket," filling micro-voids on the rigid core surface.

### Stage 2: Metabolism Factor
Evaluates the "internal health" of the material itself (Multiplier from 0.0 to 1.1).

* **Noise Penalty:** Checks the lattice axis ratio (c/a). For HCP lattices, the ideal is 1.633. Deviation (like in Zinc or Cadmium) creates internal stress and noise.
* **Decoherence Penalty:** If the volume is > 12.0 (e.g., Calcium), a penalty for "fluffiness" is applied. Signal fades in the void.
* **Plasticity Bonus:** If the material is extremely soft (Yield < 50), it gets a multiplier boost for self-healing capabilities.

### Final Formula
`Final Score = Static Score * Metabolism Factor`

## Classification
Based on the Final Score, materials are ranked:

* **LEGENDARY (Score >= 100):** Ideal partners. Perfect geometry + high plasticity (Au, Ag, Al).
* **ELITE (90-99):** Rigid but geometrically perfect partners (Pt, Pd, Mo).
* **EXCELLENT (80-89):** Solid working materials (Ta, Cu, Ti).
* **GOOD (60-79):** Compromise options (Zn, Pb).
* **RISKY (40-59):** High risk of failure due to noise or decoherence (Mg, Zr).
* **TRASH (< 40):** Thermodynamically incompatible (Ca).

## Requirements
* Python 3.x
* pandas
* numpy

## Usage
Run the script to generate the leaderboard:
`python simureality_v16.py`

## Interpretation of Results (Examples)
* **Gold (Au):** Ranked **LEGENDARY**. Despite a slight volume mismatch with Tungsten, its incredible plasticity (Metabolism Factor > 1) makes it the ultimate contact material.
* **Zinc (Zn):** Ranked **GOOD (Risky)**. Geometrically almost identical to Tungsten (High Static Score), but its distorted lattice (Noise) significantly lowers the final score. This demonstrates the algorithm's ability to detect hidden internal defects.
* **Calcium (Ca):** Ranked **TRASH**. Too fluffy to form a quantum contact with a dense metal.
