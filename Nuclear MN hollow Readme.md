# Simureality: The Centrifugal Shell — A Unified Geometric Model of Nuclear Stability

**Author:** Simureality Research Group (Pavel, et al.)  
**Version:** 3.0 (Dynamic Hamiltonian & Phase Space Analysis)

---

## 🌌 Abstract: The Duality of Nuclear Architecture

This project presents a computational verification of the **Simureality Framework**, asserting that nuclear stability (Magic Numbers) is a direct consequence of optimal geometric packing on a discrete lattice.

We resolve the long-standing discrepancy where dense-packing models successfully predict "Solid" nuclei (N=28, 56) but fail to find "Hollow" nuclei (N=20, 32). The solution is the introduction of a **Dynamic Hamiltonian** incorporating the Spin (Angular Momentum) potential.

The simulation proves that nuclei are governed by two distinct stability modes:
1.  **Crystalline Mode:** Stability driven by maximizing density (low spin).
2.  **Resonance Mode:** Stability driven by minimizing central pressure (high spin).

---

## 🔬 Methodology: The Spin-Lattice Hamiltonian

The simulation runs a **Greedy Accretion Algorithm** on a Face-Centered Cubic (FCC) lattice. The core innovation is the introduction of the $\alpha$ (Alpha) parameter, which controls the strength of the centrifugal barrier.

### 1. The Lattice and the Agent
* **Lattice:** Discrete FCC ($N_{neighbors}=12$), ensuring maximal bond potential.
* **Agent:** The nucleon, seeking the position that maximizes its total *Score*.

### 2. The Dynamic Hamiltonian (The Score Function)
The system seeks the spot where the total **Score** is maximized. This score represents the negative of the effective potential energy, combining three primary forces:

$$\text{Score} = (\text{Bonds} \times k_{\text{strong}}) - k_{\text{gravity}} \cdot r - \frac{\alpha}{r^2 + \epsilon}$$

| Term | Physical Meaning | Function in Simulation |
| :--- | :--- | :--- |
| **Bonds** | Strong Interaction (Local Attraction) | Maximizes local packing density. |
| **$-r$** | Surface Tension / Gravity (Keeps volume small) | Minimizes radius. |
| **$-\alpha/r^2$** | **Centrifugal Barrier (Spin Potential)** | Penalizes density near the center. Forces shell formation. |

### 3. The Metric: Phase Transition
We analyze the transition of the system across the **Alpha ($\alpha$) axis**. The stability of a given nucleus ($N$) is confirmed when its Gain (bonds formed) suddenly increases (a "hotspot") at the precise $\alpha$ required to support its geometric structure.

---

## 📊 Results & Interpretation (The Two Modes of Magic)

The **Spin Phase Diagram** confirms that the "Magic" list is unified, but requires two different physical contexts to manifest.

### Mode I: Crystalline Solids (Density-Driven)
These nuclei are inherently stable due to their structure, regardless of internal spin. The spin penalty ($\alpha$) merely affects their size.
* **N=28 (Nickel):** Remains highly stable at $\alpha=0$ (low spin), confirming its nature as a **Solid Monolith**. This is the geometry preferred by gravity alone.
* **N=56 (Iron):** The ultimate Monolith. Its stability is driven by maximizing the number of deep $\text{Bonds} > 5$.

### Mode II: Centrifugal Shells (Dynamics-Driven)
These nuclei are structurally unstable without a mechanism to enforce the hollow configuration.

* **N=20 (Calcium):** The simulation shows N=20 has very low stability at $\alpha=0$. **However,** it exhibits a sudden, dramatic spike in stability at a **specific, low, non-zero $\alpha$ value ($\approx 0.10$ in the log).**
    * **Interpretation:** The critical spin factor ($\alpha$) provides the precise centrifugal force necessary to push the nucleons into a stable, hollow **Dodecahedral Shell**. The nucleus is only stable at this exact **Resonance Frequency**.
    * This resolves the N=20 paradox: Calcium-40 stability is not due to pure density, but to **angular momentum stabilizing its hollow topology**.

---

## 📝 Conclusion

The **Spin Phase Scan** proves that the **Simureality Framework** can successfully model the two fundamentally different stable states found in nuclear physics:

1.  **The Monolith (N=28, 56):** Stability is maximized by structural density (packing).
2.  **The Shell (N=20, 32):** Stability is maximized by **dynamic equilibrium** (spin/centrifugal force).

This reinforces the core thesis: the laws of physics are the **algorithms of geometric optimization** running on a discrete lattice.

---

**License:** MIT  
**Contact:** Simureality Research Group
