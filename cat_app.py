import streamlit as st
import pandas as pd
import numpy as np
import itertools

# ==============================================================================
# TRILEX ORACLE v6.0: The Industrial Benchmarker
# Features: Pure, Binary, Ternary Modes + Expanded Database
# ==============================================================================

# --- PHYSICS CORE: SIMUREALITY HARMONICS ---
# "The Quarter Law": Ideal catalyst site ~ Bond Length * (2.25 or 2.5 or 3.75)
MOLECULES = {
    "Hydrogen (H2)": {
        "bond": 0.74, 
        "target_site": 2.775, # Pt (Harmonic 3.75)
        "desc": "Hydrogen Evolution (HER). Standard: Pt. Target: 2.775 A."
    },
    "Carbon Monoxide (CO)": {
        "bond": 1.12, 
        "target_site": 2.772, # Cu-Ce (Harmonic 2.5)
        "desc": "CO Oxidation. Standard: CuO-CeO2. Target: 2.772 A."
    },
    "Nitrogen (N2)": {
        "bond": 1.09, 
        "target_site": 2.480, # Fe (Harmonic 2.25)
        "desc": "Ammonia Synthesis. Standard: Fe-K. Target: 2.48 A."
    },
    "Methane (CH4)": {
        "bond": 1.09,
        "target_site": 2.720, # Ru/Rh (Harmonic 2.5)
        "desc": "C-H Activation. Hard bond. Target: 2.72 A."
    },
    "CO2 (Reduction)": {
        "bond": 1.16,
        "target_site": 2.610, # Cu is 2.55 (Too tight?), Ag is 2.89 (Too loose?)
        "desc": "CO2 to Fuels. Target: 2.61 A (Between Cu and Au)."
    },
    "NOx (Reduction)": {
        "bond": 1.15,
        "target_site": 2.580, # Rh is standard
        "desc": "Catalytic Converter. Standard: Rh. Target: 2.58 A."
    }
}

# --- HELPER FUNCTIONS ---
def get_site_distance(row):
    """Calculates active surface step based on crystal structure."""
    a = row['a_angstrom']
    struct = row['structure']
    # HCP uses 'a' as basal site, FCC uses a/sqrt(2), BCC uses a*sqrt(3)/2
    if struct == 'fcc': return a / 1.414
    if struct == 'bcc': return a * 0.866
    if struct == 'hcp': return a 
    return a 

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cat_materials.csv")
        df['site_dist'] = df.apply(get_site_distance, axis=1)
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()

def solve_alloy(components, ratios, target_site):
    # components: list of rows (dicts or series)
    # ratios: list of floats (sum=1.0)
    
    name_parts = []
    mix_site = 0
    mix_vec = 0
    mix_cost = 0
    
    for comp, r in zip(components, ratios):
        mix_site += comp['site_dist'] * r
        mix_vec += comp['vec'] * r
        mix_cost += comp['cost_index'] * r
        name_parts.append(f"{comp['element']}{int(r*100)}")
        
    alloy_name = "-".join(name_parts)
    
    # SCORING
    # 1. Geometry (Precision)
    dev = abs(mix_site - target_site)
    geo_score = np.exp(-30 * dev) * 100
    
    # 2. VEC Penalty (Activity)
    # Generally, VEC < 6 is too empty (early transition), VEC > 11 is too full (noble)
    # Sweet spot is 8-10.
    vec_penalty = 1.0
    if mix_vec < 6.0: vec_penalty = 0.6
    
    final_score = geo_score * vec_penalty
    
    return {
        "Alloy": alloy_name,
        "Site (A)": round(mix_site, 4),
        "VEC": round(mix_vec, 2),
        "Cost": round(mix_cost, 1),
        "Score": round(final_score, 1),
        "Components": [c['element'] for c in components]
    }

# --- MAIN UI ---
st.set_page_config(page_title="Trilex Oracle v6", layout="wide", page_icon="🔮")

st.title("🔮 Trilex Oracle v6.0")
st.markdown("**Simureality Engineering:** From Pure Elements to Ternary Alloys.")

df = load_data()
if df.empty: st.stop()

# SIDEBAR
st.sidebar.header("Configuration")
mode = st.sidebar.radio("Search Mode:", ["Pure Elements", "Binary Alloys", "Ternary Alloys"])
target_name = st.sidebar.selectbox("Target Reaction:", list(MOLECULES.keys()))

t_data = MOLECULES[target_name]
target_site = t_data['target_site']
st.sidebar.info(f"**Target:** {target_site} Å\n\n{t_data['desc']}")

# FILTERS
with st.sidebar.expander("Material Filters"):
    allow_noble = st.checkbox("Allow Noble (Pt, Au...)", value=False)
    allow_armor = st.checkbox("Allow Armor (Al, Ti...)", value=False)
    allow_soft = st.checkbox("Allow Soft (Zn, Pb...)", value=False)

# APPLY FILTERS
filtered_df = df.copy()
if not allow_noble: filtered_df = filtered_df[filtered_df['role'] != 'Noble']
if not allow_armor: filtered_df = filtered_df[filtered_df['role'] != 'Armor']
if not allow_soft: filtered_df = filtered_df[filtered_df['role'] != 'Soft']

st.metric("Materials available", len(filtered_df))

# RUN BUTTON
if st.button("RUN SCAN"):
    results = []
    metal_list = filtered_df.to_dict('records')
    
    progress_bar = st.progress(0)
    
    # --- MODE LOGIC ---
    
    if mode == "Pure Elements":
        # Check every single element
        for m in metal_list:
            res = solve_alloy([m], [1.0], target_site)
            results.append(res)
        progress_bar.progress(100)
            
    elif mode == "Binary Alloys":
        # Check pairs (Base + Any)
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        others = metal_list
        total_ops = len(bases) * len(others)
        idx = 0
        
        for b in bases:
            for o in others:
                if b['element'] == o['element']: continue
                # Standard ratios
                for ratio in [0.5, 0.7, 0.8, 0.9]:
                    ratios = [ratio, 1-ratio]
                    res = solve_alloy([b, o], ratios, target_site)
                    if res['Score'] > 75: results.append(res)
                idx += 1
            progress_bar.progress(min(idx / total_ops, 1.0))
            
    elif mode == "Ternary Alloys":
        # Base + Mod1 + Mod2
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        modifiers = [m for m in metal_list if m['role'] not in ['Base', 'Noble', 'Soft']]
        
        # Limit modifiers to avoid explosion
        if len(modifiers) > 15: modifiers = modifiers[:15] 
        
        total_ops = len(bases)
        idx = 0
        
        for b in bases:
            for m1, m2 in itertools.combinations(modifiers, 2):
                # Standard recipes
                recipes = [(0.7, 0.2, 0.1), (0.6, 0.2, 0.2), (0.8, 0.15, 0.05)]
                for r in recipes:
                    res = solve_alloy([b, m1, m2], r, target_site)
                    if res['Score'] > 85: results.append(res)
            idx += 1
            progress_bar.progress(min(idx / total_ops, 1.0))

    progress_bar.empty()
    
    # DISPLAY
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(50)
        
        # Highlight Top 1
        top = res_df.iloc[0]
        st.success(f"🏆 Winner: **{top['Alloy']}** | Score: {top['Score']}")
        
        st.dataframe(res_df, use_container_width=True)
        
        # Graph for context
        st.bar_chart(res_df.set_index("Alloy")['Score'].head(10))
    else:
        st.warning("No matches found. Try relaxing filters.")

