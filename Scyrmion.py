import streamlit as st
import numpy as np
import pandas as pd
import math

# --- 1. MATH CORE (No External Dependencies) ---
def is_prime_manual(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_divisors_manual(n):
    divs = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i*i != n:
                divs.append(n // i)
    return sorted(divs)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Skyrmion Pro Lab", layout="wide")

st.title("🌪️ Skyrmion Pro: Topological Engineering")
st.markdown("**Project Trilex (Simureality):** Select a material from the DB, then fine-tune parameters to find the Prime Resonance.")

# --- 3. LOAD DATABASE ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("scyrmions_db.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ Database file 'scyrmions_db.csv' not found!")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. SIDEBAR CONTROL PANEL ---
    st.sidebar.header("🎛️ Control Panel")
    
    # Legend
    with st.sidebar.expander("📚 Parameter Legend (Read Me)"):
        st.markdown("""
        **A — Stiffness (Exchange):**
        *Spring Force.* How strongly neighbors want to align.
        * High A = Stiff magnet.
        * Low A = Soft/Flexible.
        
        **D — DMI (Chirality):**
        *Twist Force.* Quantum force inducing rotation.
        * High D = Small, tight vortices.
        * Low D = Large vortices.
        
        **a — Lattice Constant:**
        *Pixel Size.* Distance between atoms.
        * The resolution of the reality grid.
        """)

    material_names = df["Material"].tolist()
    selected_name = st.sidebar.selectbox("Load Preset", material_names, key="material_selector")
    
    row = df[df["Material"] == selected_name].iloc[0]
    
    # SESSION STATE LOGIC
    if "last_selected_mat" not in st.session_state:
        st.session_state.last_selected_mat = None

    if st.session_state.last_selected_mat != selected_name:
        st.session_state.last_selected_mat = selected_name
        st.session_state.A_input = float(row["A_stiffness"])
        st.session_state.D_input = float(row["D_dmi"])
        st.session_state.a_input = float(row["a_lattice"])
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write("⚙️ **Fine-Tuning (High Precision)**")
    
    # Input Fields (4 decimal places)
    A_val = st.sidebar.number_input("Stiffness A (pJ/m)", step=0.001, format="%.4f", key="A_input")
    D_val = st.sidebar.number_input("DMI D (mJ/m²)", step=0.001, format="%.4f", key="D_input")
    a_val = st.sidebar.number_input("Lattice a (nm)", step=0.0001, format="%.4f", key="a_input")

    mat_type = str(row['Type'])
    mat_desc = str(row['Description'])
    st.sidebar.info(f"**Type:** {mat_type}\n\n{mat_desc}")

    # --- 5. CALCULATION ENGINE ---
    if D_val == 0: D_val = 0.0001
    # Physics: Helical Pitch L = 4*pi*A / D
    pitch_nm = (4 * np.pi * A_val) / D_val
    radius_nm = pitch_nm / 2

    # Simureality Geometry
    area_skyrmion = np.pi * (radius_nm ** 2)
    area_node = a_val ** 2
    num_nodes_raw = area_skyrmion / area_node
    num_nodes = int(round(num_nodes_raw))

    is_prime = is_prime_manual(num_nodes)
    divisors = get_divisors_manual(num_nodes)
    num_divs = len(divisors)

    # --- 6. MAIN DISPLAY ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vortex Radius (R)", f"{radius_nm:.4f} nm")
    with col2:
        preset_pitch = (4 * np.pi * row["A_stiffness"]) / row["D_dmi"]
        preset_nodes = int(round((np.pi * (preset_pitch/2)**2) / row["a_lattice"]**2))
        diff_nodes = num_nodes - preset_nodes
        
        if diff_nodes > 0:
            delta_str = f"+{diff_nodes} vs Preset"
            delta_color = "normal"
        elif diff_nodes < 0:
            delta_str = f"{diff_nodes} vs Preset"
            delta_color = "off"
        else:
            delta_str = "Exact Preset"
            delta_color = "off"
        
        st.metric("Grid Nodes (N)", f"{num_nodes}", delta=delta_str, delta_color=delta_color)
        
    with col3:
        if is_prime:
            st.success("💎 PRIME FOUND")
        elif num_divs <= 4:
            st.warning("💾 ROBUST")
        else:
            st.error("⚠️ UNSTABLE")

    st.divider()

    st.subheader("Simureality Verdict")
    
    if is_prime:
        st.success(f"### 💎 PRIME TOPOLOGY DETECTED: {num_nodes}")
        st.markdown(f"**Status: ABSOLUTE STABILITY.**\n\nThe geometry of {selected_name} (with current settings) forms an indestructible Prime Knot.")
    else:
        # Find Target
        lower_prime = num_nodes - 1
        while not is_prime_manual(lower_prime): lower_prime -= 1
        upper_prime = num_nodes + 1
        while not is_prime_manual(upper_prime): upper_prime += 1
        
        dist_down = num_nodes - lower_prime
        dist_up = upper_prime - num_nodes
        target = lower_prime if dist_down < dist_up else upper_prime
        diff = target - num_nodes
        
        # Display Status
        if num_divs <= 4 and num_nodes % 2 == 0:
             st.info(f"### 💾 SEMI-PRIME: {num_nodes} = 2 × {num_nodes//2}")
             st.write("Status: **Rewritable Memory** (Semi-Stable).")
        else:
             st.error(f"### ⚠️ COMPOSITE: {num_nodes} ({num_divs} divisors)")
             st.write("Status: **Instability / Decay**.")

        # --- OPTIMIZATION LOGIC ---
        st.markdown(f"**Optimization Strategy:** Nearest Prime Attractor is **{target}** (Diff: {diff}).")
        
        # Calculate Exact A required for the target
        # N ~ A^2  =>  A_new = A_old * sqrt(N_target / N_current)
        if num_nodes > 0:
            optimal_A = A_val * math.sqrt(target / num_nodes)
        else:
            optimal_A = A_val # Safety

        col_opt1, col_opt2 = st.columns([3, 1])
        with col_opt1:
             st.caption(f"👉 Required Stiffness A ≈ **{optimal_A:.4f}**")
        with col_opt2:
             if st.button(f"✨ Auto-Optimize"):
                 st.session_state.A_input = optimal_A
                 st.rerun()

    # --- 7. LANDSCAPE ---
    st.write("---")
    st.write("⛰️ **Stability Landscape**")
    
    range_width = 15
    start_x = max(1, num_nodes - range_width)
    end_x = num_nodes + range_width
    
    x_vals = list(range(start_x, end_x + 1))
    y_vals = []
    
    for x in x_vals:
        if x == num_nodes:
            val = 50 
        elif is_prime_manual(x):
            val = 100
        else:
            d = len(get_divisors_manual(x))
            val = max(5, 85 - d*8)
        y_vals.append(val)

    chart_data = pd.DataFrame({"Nodes": x_vals, "Stability Index": y_vals})
    st.bar_chart(chart_data.set_index("Nodes"))

else:
    st.warning("⚠️ Database not loaded.")
