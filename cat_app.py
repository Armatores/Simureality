import streamlit as st
import pandas as pd
import numpy as np
import itertools

# ==============================================================================
# SIMUREALITY: GEOMETRIC CATALYST SCANNER (GCS) v7.5
# Framework: Grid Physics / Simureality Engineering
# License: GNU GPL v2.0
# Focus: 3D Lattice Interpolation & Topological Debt Minimization
# ==============================================================================

# --- CORE PHYSICS: TARGET MOLECULES & BOND SITES ---
MOLECULES = {
    "Hydrogen (H2)": {
        "bond": 0.74, "target_site": 2.775, "ref": "Pt (Harmonic 3.75)",
        "desc": "Standard: Pt. Target: 2.775 Å."
    },
    "Carbon Monoxide (CO)": {
        "bond": 1.12, "target_site": 2.772, "ref": "Cu-Ce (Harmonic 2.5)",
        "desc": "Standard: CuO-CeO2. Target: 2.772 Å."
    },
    "Nitrogen (N2)": {
        "bond": 1.09, "target_site": 2.480, "ref": "Fe (Harmonic 2.25)",
        "desc": "Standard: Fe-K. Target: 2.48 Å."
    },
    "Methane (CH4)": {
        "bond": 1.09, "target_site": 2.720, "ref": "Rh (Harmonic 2.5)",
        "desc": "Standard: Rh. Target: 2.72 Å."
    },
    "CO2 (Reduction)": {
        "bond": 1.16, "target_site": 2.610, "ref": "Cu/Au boundary",
        "desc": "Target: 2.61 Å."
    },
    "NOx (Reduction)": {
        "bond": 1.15, "target_site": 2.580, "ref": "Rh",
        "desc": "Standard: Rh. Target: 2.58 Å."
    },
    "Oxygen Reduction (ORR)": {
        "bond": 1.21, "target_site": 2.700, "ref": "Pt3Ni",
        "desc": "Fuel cells. Standard: Pt-Ni. Target: 2.70 Å."
    },
    "Hydrogen Evolution (HER)": {
        "bond": 0.74, "target_site": 2.740, "ref": "Pt / MoS2",
        "desc": "Water splitting. Target: 2.74 Å."
    },
    "Ethylene Epoxidation": {
        "bond": 1.34, "target_site": 2.890, "ref": "Ag",
        "desc": "Standard: Ag. Target: 2.89 Å."
    },
    "Lithium (Intercalation)": {
        "bond": 2.67, "target_site": 3.040, "ref": "BCC Li distance",
        "desc": "Solid-state battery anodes. Target: 3.040 Å."
    }
}

# --- ARCHITECTURAL HELPER FUNCTIONS ---
def get_site_distance(row):
    """Calculates the 3D distance between nodes based on lattice structure."""
    a = row['a_angstrom']
    struct = row['structure']
    if struct == 'fcc': return a / 1.414  # Nearest neighbor in FCC
    if struct == 'bcc': return a * 0.866  # Nearest neighbor in BCC
    if struct == 'hcp': return a          # Basal plane distance
    return a 

@st.cache_data
def load_data():
    """Loads the elemental database and calculates baseline site distances."""
    try:
        # Expected columns: element, a_angstrom, structure, role, vec, cost_index
        df = pd.read_csv("cat_materials.csv")
        df['site_dist'] = df.apply(get_site_distance, axis=1)
        return df
    except Exception as e:
        st.error(f"Error loading cat_materials.csv: {e}")
        return pd.DataFrame()

def get_risk_tags(components, target_name):
    """Applies hazard flags based on chemical incompatibility and high costs."""
    tags = []
    elems = [c['element'] for c in components]
    roles = [c['role'] for c in components]
    
    # 1. EXPLOSIVE HAZARD
    if 'C' in elems and any(x in elems for x in ['Ag', 'Au', 'Cu']):
        tags.append("☢️")
    
    # 2. INERTNESS (Noble vs Hard Bonds)
    if target_name in ["Nitrogen (N2) Fixation", "Methane (CH4) Activation"]:
        base_vec = components[0]['vec']
        if base_vec >= 10.5 and not any(x in elems for x in ['Fe', 'Ru', 'Os', 'Re']):
            tags.append("❄️")

    if 'Armor' in roles: tags.append("🛡️")
    if 'Soft' in roles: tags.append("💧")
    
    costs = [c['cost_index'] for c in components]
    if max(costs) > 100: tags.append("💰")
        
    return tags

def solve_alloy(components, ratios, target_site, target_name, ignore_risks):
    """Core Engine: Solves for interpolated site distance and geometric score."""
    mix_site = sum([c['site_dist'] * r for c, r in zip(components, ratios)])
    mix_vec = sum([c['vec'] * r for c, r in zip(components, ratios)])
    
    name_parts = [f"{c['element']}{int(r*100)}" for c, r in zip(components, ratios)]
    alloy_name = "-".join(name_parts)
    
    # Deviation from ideal geometric site
    dev = abs(mix_site - target_site)
    geo_score = np.exp(-30 * dev) * 100  # Exponential decay of accuracy
    
    tags = get_risk_tags(components, target_name)
    
    penalty = 1.0
    if not ignore_risks:
        if "☢️" in tags: penalty *= 0.0  # Lethal hazard
        if "❄️" in tags: penalty *= 0.1  # Inefficient
        if "💧" in tags: penalty *= 0.5  # Low melting point
        
    final_score = geo_score * penalty
    
    return {
        "Alloy": alloy_name,
        "Site (A)": round(mix_site, 4),
        "VEC": round(mix_vec, 2),
        "Score": round(final_score, 1),
        "Hazards": " ".join(tags),
    }

# --- UI LAYOUT ---
st.set_page_config(page_title="Simureality GCS", layout="wide", page_icon="🧊")

st.title("🧊 Simureality: Geometric Catalyst Scanner")
st.markdown("**Simureality Engineering Framework:** Heuristic 3D-Lattice Interpolation.")

# Theoretical Manifest
with st.expander("ℹ️ Architectural Concept (The Grid Physics Approach)"):
    st.markdown("""
    In the **Simureality** framework, heterogeneous catalysis is viewed as a hardware interface problem. 
    Instead of modeling electron clouds (DFT), this scanner calculates the **interpolated 3D lattice site distances** of alloys. 
    
    **Goal:** Minimize the **Topological Debt (ΔK)** by matching the alloy's surface geometry to the molecule's optimal bond length. 
    When the geometric 'puzzle' fits perfectly, the activation energy drops significantly.
    """)

df = load_data()
if df.empty: 
    st.error("Missing 'cat_materials.csv'. Please provide the elemental database.")
    st.stop()

# --- SIDEBAR: STRATEGY & PARAMETERS ---
st.sidebar.header("1. Strategy")
mode = st.sidebar.radio("Search Mode:", ["Pure Elements", "Binary Alloys", "Ternary Alloys"])
target_name = st.sidebar.selectbox("Target Reaction:", list(MOLECULES.keys()))
t_data = MOLECULES[target_name]

st.sidebar.info(f"**Target Site:** {t_data['target_site']} Å  \n*Ref: {t_data['ref']}*")

st.sidebar.header("2. Ingredients")
c1, c2 = st.sidebar.columns(2)
allow_noble = c1.checkbox("Noble Metals", value=True)
allow_armor = c1.checkbox("Armor (d-block)", value=True)
allow_soft = c2.checkbox("Soft Metals", value=False)
allow_dwarf = c2.checkbox("Dwarfs", value=True)

ignore_risks = st.sidebar.checkbox("Ignore Chemical Hazards", value=True)

# FILTERING DATA
filtered_df = df.copy()
if not allow_noble: filtered_df = filtered_df[filtered_df['role'] != 'Noble']
if not allow_armor: filtered_df = filtered_df[filtered_df['role'] != 'Armor']
if not allow_soft: filtered_df = filtered_df[filtered_df['role'] != 'Soft']
if not allow_dwarf: filtered_df = filtered_df[filtered_df['role'] != 'Dwarf']

# SIDEBAR FOOTER
with st.sidebar.expander("Risk Legend"):
    st.markdown("☢️ Explosive | ❄️ Inert | 🛡️ Heavy Oxide | 💧 Soft/Melts | 💰 High Cost")

st.sidebar.divider()
st.sidebar.markdown("""
**License:** [GPL-2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)  
Open Source. Powered by Simureality Theory.
""")

# --- MAIN ENGINE LOOP ---
if st.button("RUN GEOMETRIC SCAN"):
    results = []
    metal_list = filtered_df.to_dict('records')
    progress_bar = st.progress(0)
    
    # 1. PURE ELEMENTS
    if mode == "Pure Elements":
        for m in metal_list:
            results.append(solve_alloy([m], [1.0], t_data['target_site'], target_name, ignore_risks))
        progress_bar.progress(100)
            
    # 2. BINARY ALLOYS (Full Ratio Scan 10-90%)
    elif mode == "Binary Alloys":
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        others = metal_list
        if not bases: bases = metal_list
        
        total = len(bases)
        for i, b in enumerate(bases):
            for o in others:
                if b['element'] == o['element']: continue
                for r_val in range(1, 10):
                    r = r_val / 10.0
                    results.append(solve_alloy([b, o], [r, 1-r], t_data['target_site'], target_name, ignore_risks))
            progress_bar.progress((i+1)/total)
            
    # 3. TERNARY ALLOYS (Fast Heuristic Scan)
    elif mode == "Ternary Alloys":
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        modifiers = [m for m in metal_list if m['role'] != 'Soft']
        active_mods = modifiers[:20] # Limit for speed
        
        total = len(bases)
        for i, b in enumerate(bases):
            for m1, m2 in itertools.combinations(active_mods, 2):
                # Standard 70-20-10 ratio for stability
                results.append(solve_alloy([b, m1, m2], [0.7, 0.2, 0.1], t_data['target_site'], target_name, ignore_risks))
            progress_bar.progress((i+1)/total)

    progress_bar.empty()
    
    # DISPLAY RESULTS
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(100)
        
        top = res_df.iloc[0]
        st.success(f"🏆 Champion Candidate: **{top['Alloy']}** (Geometric Score: {top['Score']})")
        
        st.dataframe(
            res_df[['Alloy', 'Score', 'Site (A)', 'VEC', 'Hazards']], 
            use_container_width=True,
            height=600,
            column_config={
                "Score": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
            }
        )
    else:
        st.error("No valid alloys found with current filters.")
