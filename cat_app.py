import streamlit as st
import pandas as pd
import numpy as np
import itertools

# ==============================================================================
# TRILEX ORACLE: CATALYST DESIGNER (Streamlit Version)
# Architecture: Simureality Research Group
# ==============================================================================

# --- PHYSICS CONSTANTS ---
PLATINUM_SITE = 2.775  # The Gold Standard for H2
CU_CE_SITE = 2.772     # The Gold Standard for CO

# --- MOLECULE DATABASE (The Lock) ---
MOLECULES = {
    "Hydrogen (H2)": {
        "bond": 0.74, 
        "target_site": 2.775, # Matches Pt
        "desc": "Hydrogen Evolution (HER). Requires Geometry ~2.77 A."
    },
    "Carbon Monoxide (CO)": {
        "bond": 1.12, 
        "target_site": 2.772, # Matches Cu-Ce
        "desc": "CO Oxidation / Methanol. Requires Geometry ~2.77 A."
    },
    "Nitrogen (N2)": {
        "bond": 1.09, 
        "target_site": 2.480, # Matches Fe (Haber-Bosch)
        "desc": "Ammonia Synthesis. Requires tight grip ~2.48 A."
    },
    "Oxygen (O2)": {
        "bond": 1.21, 
        "target_site": 2.600, # Approx Ru/Ir
        "desc": "Fuel Cells / Electrolysis. Requires ~2.60 A."
    },
    "C-C Bond (Plastics)": {
        "bond": 1.54,
        "target_site": 1.54 * 1.2, # Harmonic 1.2 rule
        "desc": "Plastic Depolymerization. Experimental."
    }
}

# --- HELPER FUNCTIONS ---
def get_site_distance(row):
    """Calculates active surface step based on crystal structure."""
    a = row['a_angstrom']
    struct = row['structure']
    if struct == 'fcc': return a / 1.414     # a / sqrt(2)
    if struct == 'bcc': return a * 0.866     # a * sqrt(3) / 2
    return a # Default for hcp/other

def load_data():
    """Loads the material database."""
    try:
        df = pd.read_csv("cat_materials.csv")
        # Pre-calculate site distance for speed
        df['site_dist'] = df.apply(get_site_distance, axis=1)
        return df
    except FileNotFoundError:
        st.error("File 'cat_materials.csv' not found. Please create it first!")
        return pd.DataFrame()

# --- CORE LOGIC ---
def solve_alloy(base, m1, m2, ratios, target_site):
    # Unpack ratios
    r_b, r_1, r_2 = ratios
    
    # 1. Geometric Mix (Vegard's Law on Site Distance)
    # This simulates the average surface topology
    mix_site = (base['site_dist'] * r_b) + (m1['site_dist'] * r_1) + (m2['site_dist'] * r_2)
    
    # 2. VEC Mix (Electronic Structure)
    mix_vec = (base['vec'] * r_b) + (m1['vec'] * r_1) + (m2['vec'] * r_2)
    
    # 3. Cost Mix
    mix_cost = (base['cost_index'] * r_b) + (m1['cost_index'] * r_1) + (m2['cost_index'] * r_2)
    
    # --- SIMUREALITY SCORING ---
    # Geometry Score: Exponential precision required
    dev = abs(mix_site - target_site)
    geo_score = np.exp(-30 * dev) * 100
    
    # Electronic Score: Catalyst Needs Electrons (VEC > 7 is usually preferred for activity)
    vec_penalty = 1.0
    if mix_vec < 6.5: vec_penalty = 0.5 # Too empty d-shell
    
    final_score = geo_score * vec_penalty
    
    return {
        "Alloy": f"{base['element']}{int(r_b*100)}-{m1['element']}{int(r_1*100)}-{m2['element']}{int(r_2*100)}",
        "Site (A)": round(mix_site, 4),
        "VEC": round(mix_vec, 2),
        "Cost": round(mix_cost, 1),
        "Score": round(final_score, 1),
        "Base": base['element'],
        "M1": m1['element'],
        "M2": m2['element']
    }

# --- UI ---
st.set_page_config(page_title="Trilex Catalyst Oracle", layout="wide")

st.title("🧪 Project Trilex: Catalyst Oracle")
st.markdown("**Simureality Engineering:** Finding Geometric Resonance in Alloys.")

# 1. Load Data
df = load_data()
if df.empty: st.stop()

# 2. Sidebar Controls
st.sidebar.header("1. Target")
target_name = st.sidebar.selectbox("Select Reaction:", list(MOLECULES.keys()))
target_data = MOLECULES[target_name]
target_site = target_data['target_site']

st.sidebar.info(f"**Target Geometry:** {target_site} Å\n\n{target_data['desc']}")

st.sidebar.header("2. Filters")
allow_noble = st.sidebar.checkbox("Allow Noble Metals (Pt, Pd...)", value=False)
allow_armor = st.sidebar.checkbox("Allow Oxide Armor (Al, Ti...)", value=False)
allow_soft = st.sidebar.checkbox("Allow Soft Metals (Zn, Pb...)", value=False)

# 3. Filtering Logic
filtered_df = df.copy()
if not allow_noble: filtered_df = filtered_df[filtered_df['role'] != 'Noble']
if not allow_armor: filtered_df = filtered_df[filtered_df['role'] != 'Armor']
if not allow_soft:  filtered_df = filtered_df[filtered_df['role'] != 'Soft']

st.write(f"Scanning **{len(filtered_df)}** elements for optimal ternary combinations...")

# 4. The Algorithm
if st.button("RUN ORACLE SCAN"):
    results = []
    
    # Categorize available elements
    bases = filtered_df[filtered_df['role'].isin(['Base', 'Noble'])]
    modifiers = filtered_df[filtered_df['role'].isin(['Giant', 'Scaffold', 'Armor', 'Soft'])]
    
    # Progress bar
    progress_bar = st.progress(0)
    
    # Optimized Loops: Base + Mod1 + Mod2
    # We assume Base is dominant (60-90%)
    
    # Standard ternary ratios to test
    ratios_list = [
        (0.70, 0.20, 0.10), # Balanced Doping
        (0.80, 0.15, 0.05), # Light Doping
        (0.60, 0.20, 0.20)  # Heavy Mixing
    ]
    
    total_ops = len(bases) * len(modifiers) * len(modifiers)
    current_op = 0
    
    # Convert to list of dicts for faster iteration
    base_records = bases.to_dict('records')
    mod_records = modifiers.to_dict('records')
    
    for base in base_records:
        # Combinations of modifiers
        for m1, m2 in itertools.combinations(mod_records, 2):
            for ratios in ratios_list:
                res = solve_alloy(base, m1, m2, ratios, target_site)
                if res['Score'] > 80.0: # Filter noise
                    results.append(res)
        
        # Update progress roughly
        current_op += len(modifiers)**2
        prog = min(current_op / total_ops, 1.0)
        progress_bar.progress(prog)
        
    progress_bar.empty()
    
    # 5. Results Display
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
        
        # Top Candidate Highlight
        top = res_df.iloc[0]
        st.success(f"🏆 Top Candidate: **{top['Alloy']}** (Score: {top['Score']})")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Site Distance", f"{top['Site (A)']} Å", delta=f"{round(top['Site (A)'] - target_site, 4)}")
        col2.metric("VEC", top['VEC'])
        col3.metric("Cost Index", top['Cost'])
        
        st.subheader("Top 20 Candidates")
        st.dataframe(res_df.head(20), use_container_width=True)
        
        # Download
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full Report", csv, "trilex_catalysts.csv", "text/csv")
        
    else:
        st.warning("No high-performance alloys found with current filters. Try allowing Noble metals or changing the target.")

