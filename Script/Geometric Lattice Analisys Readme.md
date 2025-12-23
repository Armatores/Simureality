# Simureality V12: The Geometric Auditor

## Description
This script serves as the **Diagnostic Engine** of the Simureality project. While other versions attempt to predict properties, V12 performs a **Reverse Engineering Audit** of known physical constants.

**Objective:** To calculate the exact "Energy Tax" that the universe levies on different materials.

By comparing the **Theoretical Geometric Energy** (derived purely from lattice geometry and ionization) against the **Experimental Work Function** (measured in labs), this script quantifies the entropy of specific elements. It transforms "prediction errors" into "measurable data points" regarding material efficiency.

## Theoretical Basis
The script operates on the **Conservation of Complexity** principle:

* **Input:** Ionization Energy ($I$) represents the raw potential of an atom.
* **Ideal Processing:** A perfect crystal lattice should convert this energy with a specific geometric efficiency:
    * **FCC Efficiency:** $\phi \approx 0.618$ (Golden Ratio conjugate).
    * **BCC Efficiency:** $1 / \sqrt{3} \approx 0.577$.
* **Reality Check:** The Real Work Function ($WF_{real}$) is always lower than the Ideal.
* **The Discovery:** The difference ($Gap$) is not random error. It is the cost of **Entropy Metabolism**.

## Algorithm Logic
The script processes the dataset with the following logic:

### 1. Calculate Geometric Ideal
$$Ideal = Ionization \times GeometricFactor$$

### 2. Calculate The Gap (Delta)
$$\Delta = Ideal - RealWF$$

### 3. Derive the Tax Coefficient
$$ImpliedTax = \frac{\Delta}{Ideal}$$

## Key Findings (The "System Tax")
The output of V12 revealed three distinct classes of entropy:

* **The System Baseline (Hardcoded Tax):** Dense, rigid metals like Tungsten (W) and Molybdenum (Mo) show a consistent energy loss of approximately **4.18%**. This suggests a fundamental "Vacuum Impedance" or "System Tax" inherent to the simulation grid itself, independent of the material.
* **Dissipation Tax (Plasticity):** Soft metals like Gold (Au) and Copper (Cu) show a significantly higher tax (10-15%). The script identifies this excess loss as energy converted into phonon vibrations (heat) to maintain structural plasticity.
* **Decoherence Tax (Volume):** Low-density materials like Calcium (Ca) show massive losses (>30%). The script correlates this directly to Molar Volume, proving that "fluffy" lattices lose quantum coherence.

## Requirements
* Python 3.x
* pandas
* numpy

## Usage
Run the analysis:
`python simureality_v12.py`
