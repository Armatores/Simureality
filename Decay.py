import streamlit as st
import pandas as pd
import numpy as np

# --- SIMUREALITY ONTOLOGICAL CONSTANTS ---
GAMMA_SYS = 1.0418          # System Tax for 3D rendering (Desynchronization penalty)
JITTER_COST = 0.0131        # Dynamic noise energy per unclosed open port (MeV)
MAGIC_NUMBERS = [2, 8, 20, 28, 50, 82, 126, 184] # Ideal geometric FCC assemblies

st.set_page_config(page_title="Grid Physics: f_grid Topology Compiler", layout="wide")

def get_asymmetry(nucleons):
    """
    Calculates the number of uncompensated ports relative to 
    the nearest ideal geometric assembly (Magic Number).
    """
    distances = [abs(nucleons - m) for m in MAGIC_NUMBERS]
    return min(distances)

def compile_f_grid(Z, N):
    """
    Discrete Grid Physics equivalent of B. Krieger's f_comp(G).
    Calculates the balancing of open routing ports in the nucleus.
    """
    asym_Z = get_asymmetry(Z)
    asym_N = get_asymmetry(N)
    
    # Total vector asymmetry (unclosed ports)
    total_asymmetry = asym_Z + asym_N
    
    # Grid Compensation Function
    # If asymmetry = 0, f_grid = 1.0 (Perfect FCC / Platonic closure)
    f_grid = 1.0 - (total_asymmetry * JITTER_COST * GAMMA_SYS)
    
    # Calculation of decay probability (Topological Debt)
    # The greater the asymmetry, the faster the buffer overflows
    topological_debt = total_asymmetry * (GAMMA_SYS ** total_asymmetry)
    
    return f_grid, total_asymmetry, topological_debt, asym_Z, asym_N

# --- INTERFACE ---
st.title("🌌 Grid Physics: Discrete Topology Compiler ($f_{grid}$)")
st.markdown("""
**A discrete hardware perspective on continuous nuclear topology.** In Grid Physics, $f_{grid} = 1.0$ signifies an optimal FCC lattice closure (zero uncompensated ports), mirroring the hyper-symmetric closures found in continuous Skyrmion models.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("Node Input Data")
    Z = st.number_input("Protons (Z)", min_value=1, max_value=120, value=82, step=1)
    N = st.number_input("Neutrons (N)", min_value=1, max_value=184, value=126, step=1)
    
with col2:
    st.header("Matrix System Monitor")
    f_grid, total_asym, debt, a_z, a_n = compile_f_grid(Z, N)
    
    # Status Visualization
    if total_asym == 0:
        st.success("✅ STATUS: PERFECT CLOSURE (Doubly Magic Nucleus)")
        st.info("Geometry is perfectly balanced. All hardware ports are closed. f_grid = 1.0")
    elif a_z == 0 or a_n == 0:
        st.warning("⚠️ STATUS: PARTIAL CLOSURE (Magic Nucleus)")
        st.write("One sub-lattice is balanced, but overall topological jitter remains.")
    else:
        st.error("🚨 STATUS: ASYMMETRY DETECTED (Unstable Nucleus)")
        st.write("Topological debt is accumulating. High probability of decay (Garbage Collection).")

st.markdown("---")
st.subheader("📊 Compiler Logs")

m1, m2, m3, m4 = st.columns(4)
m1.metric("f_grid (Compensation)", f"{f_grid:.4f}")
m2.metric("Uncompensated Voxels", f"{total_asym}")
m3.metric("Topological Debt (ΣK)", f"{debt:.2f}")
m4.metric("Jitter Penalty", f"-{(total_asym * JITTER_COST):.4f} MeV")

st.markdown("""
### Grid Physics approach to B. Krieger's $f_{comp}(G)$ model:
In continuous Skyrmion theory, proving $f_{comp} = 1$ (e.g., for Lead-208) requires integration of $SO(3)$ rotation matrices to demonstrate the vanishing of low-rank multipole moments. 

**The Grid Physics Perspective:** We can map this continuous topological stability directly onto discrete hardware constraints. Magic numbers represent perfect graph closures on a Face-Centered Cubic (FCC) lattice. At $Z=82$ and $N=126$, the number of uncompensated routing vectors drops to zero, inherently preventing the emission of topological jitter. Both models arrive at the same stability peaks—one via continuous geometry, the other via discrete computational routing constraints.
""")
