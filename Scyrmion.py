import streamlit as st
import numpy as np
import sympy

# --- SIMUREALITY CORE CONFIG ---
SYSTEM_TAX = 1.0418  # Gamma_sys
GRID_IMPEDANCE = 137.036 # Lattice Impedance

# --- PRESET MATERIALS (Standard Data from Literature) ---
# A = Exchange Stiffness (pJ/m), D = DMI Constant (mJ/m^2), a = Lattice Const (nm)
MATERIALS = {
    "FeGe (Helimagnet)": {"A": 8.78, "D": 1.58, "a": 0.47},
    "MnSi (Classic)":    {"A": 4.4,  "D": 0.72, "a": 0.456},
    "Co-Zn-Mn (Room Temp)": {"A": 6.2, "D": 2.1, "a": 0.64},
    "Custom":            {"A": 10.0, "D": 1.5,  "a": 0.5}
}

st.set_page_config(page_title="Skyrmion Prime Screener", layout="wide")

st.title("🌪️ Project Trilex: Skyrmion Stability Screener")
st.markdown(f"**Core Hypothesis:** Topological stability is governed by the Primality of the Lattice Node Count involved in the vortex.")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("🔬 Material Parameters")
selected_mat = st.sidebar.selectbox("Choose Host Material", list(MATERIALS.keys()))

if selected_mat == "Custom":
    A_val = st.sidebar.number_input("Exchange Stiffness A (pJ/m)", 0.1, 50.0, 10.0)
    D_val = st.sidebar.number_input("DMI Constant D (mJ/m²)", 0.01, 10.0, 1.5)
    a_val = st.sidebar.number_input("Lattice Constant a (nm)", 0.1, 2.0, 0.5)
else:
    params = MATERIALS[selected_mat]
    A_val = params["A"]
    D_val = params["D"]
    a_val = params["a"]
    st.sidebar.markdown(f"**Loaded Params for {selected_mat}:**")
    st.sidebar.code(f"A = {A_val}\nD = {D_val}\na = {a_val}")

# --- CALCULATION ENGINE ---

# 1. Theoretical Radius (Standard Model Approximation)
# R = pi * D / A is a rough scaling, but typically R ~ A/D or D/A depending on units.
# Correct scaling for simple estimation: R ≈ π * A / D (CHECK UNITS!)
# Let's use the characteristic length L_D = 4*pi*A / D
# Radius is usually approx L_D / 2.
# Let's stick to simple geometric balance:
try:
    # A in pJ/m (10^-12), D in mJ/m^2 (10^-3).
    # We need result in nm.
    # Let's normalize to nm scale units.
    A_norm = A_val  # pJ/m
    D_norm = D_val  # mJ/m^2
    
    # Characteristic Period (Pitch)
    # L = 4 * pi * A / D
    # Example FeGe: 4 * 3.14 * 8.78 / 1.58 = ~70 nm (Matches literature ~70nm)
    helical_pitch = (4 * np.pi * A_norm) / D_norm 
    
    # Skyrmion Radius is typically Half the Pitch (or slightly less due to Tax)
    sky_radius = (helical_pitch / 2) 
    
    # Apply System Tax?
    # Hypothesis: The standard formula assumes continuous space. 
    # Real grid is tighter. The Tax compresses the radius? Or expands?
    # Let's calculate RAW first.
    
except ZeroDivisionError:
    st.error("DMI cannot be zero for Skyrmions.")
    st.stop()

# 2. Geometry Counting
sky_area = np.pi * (sky_radius ** 2)
unit_cell_area = (a_val ** 2)

# Number of Unit Cells (Nodes) in the Vortex
# This is our key integer
num_nodes_raw = sky_area / unit_cell_area
num_nodes_int = int(round(num_nodes_raw))

# 3. Primality Check
is_prime = sympy.isprime(num_nodes_int)

# 4. Divisibility Analysis (if not prime)
divisors = sympy.divisors(num_nodes_int)
symmetry_score = 0
if not is_prime:
    # More divisors = More ways to fold/collapse = Less Stable
    # Score 0 = Bad (Highly composite), Score 100 = Prime
    num_divs = len(divisors)
    # Heuristic: Prime has 2 divisors (1 and itself). 
    # Highly composite (like 100) has 9.
    symmetry_score = max(0, 100 - (num_divs * 10))
else:
    symmetry_score = 100 # Maximum Stability (Indivisible)

# --- DISPLAY RESULTS ---

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Helical Pitch (L)", f"{helical_pitch:.2f} nm")
    st.metric("Vortex Radius (R)", f"{sky_radius:.2f} nm")

with col2:
    st.metric("Lattice Constant", f"{a_val} nm")
    st.metric("Grid Nodes Involved", f"{num_nodes_int}")

with col3:
    if is_prime:
        st.success("## 🛡️ PRIME TOPOLOGY")
        st.markdown("**Status: EXTREMELY STABLE**")
        st.write("The vortex locks onto a Prime Number of lattice nodes. It cannot be geometrically folded.")
    else:
        if symmetry_score < 40:
            st.error("## ⚠️ COMPOSITE WEAKNESS")
            st.markdown("**Status: UNSTABLE / DECAY**")
        else:
            st.warning("## 🔸 METASTABLE")
            st.markdown("**Status: CONDITIONAL**")
        st.write(f"Divisors found: {len(divisors)}")
        st.caption(f"Geometry can shatter into: {divisors}")

st.divider()

# --- THE SIMUREALITY ANALYSIS ---
st.subheader("🤖 The Simureality Verdict")

# Finding the nearest Prime Target
lower_prime = sympy.prevprime(num_nodes_int)
upper_prime = sympy.nextprime(num_nodes_int)

dist_down = num_nodes_int - lower_prime
dist_up = upper_prime - num_nodes_int

st.write(f"Current Lattice Load: **{num_nodes_int} nodes**")

if is_prime:
    st.balloons()
    st.markdown(f"""
    > **System Analysis:** The Skyrmion has naturally formed a **Prime Knot ({num_nodes_int})**. 
    > According to the **Prime Stability Hypothesis**, this magnetic structure is protected by number theory. 
    > No supercomputer needed: This material is a perfect candidate for memory.
    """)
else:
    target = lower_prime if dist_down < dist_up else upper_prime
    change_needed = "Shrink" if target == lower_prime else "Expand"
    
    st.markdown(f"""
    > **System Analysis:** This structure is geometrically vulnerable (Composite).
    > **Prediction:** The Skyrmion will likely deform or drift to reach the nearest Prime Attractor: **{target} nodes**.
    > **Optimization:** Try adjusting the magnetic field to {change_needed} the radius slightly.
    """)

# --- VISUALIZATION (THE NAPKIN) ---
# Simple plot of the "Stability Landscape" around current value
x_range = np.arange(num_nodes_int - 20, num_nodes_int + 21)
y_stability = []

for x in x_range:
    if x <= 0:
        y_stability.append(0)
    elif sympy.isprime(int(x)):
        y_stability.append(100)
    else:
        # Penalize by number of divisors
        d = len(sympy.divisors(int(x)))
        y_stability.append(max(10, 80 - d*5))

chart_data = {"Nodes": x_range, "Stability Index": y_stability}
st.bar_chart(chart_data, x="Nodes", y="Stability Index")
st.caption("Peaks = Prime Numbers (Stable Configurations). Valleys = Composite Numbers (Instability).")

