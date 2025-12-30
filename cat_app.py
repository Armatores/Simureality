import streamlit as st
import pandas as pd
import numpy as np
import itertools

# ==============================================================================
# TRILEX ORACLE v7.0: UNCHAINED POTENTIAL
# Philosophy: Pure Geometric Resonance first. Chemical Reality check second.
# ==============================================================================

# --- PHYSICS CORE ---
MOLECULES = {
    "Hydrogen (H2)": {
        "bond": 0.74, "target_site": 2.775, "ref": "Pt (Harmonic 3.75)",
        "desc": "Hydrogen Evolution. Standard: Pt."
    },
    "Carbon Monoxide (CO)": {
        "bond": 1.12, "target_site": 2.772, "ref": "Cu-Ce (Harmonic 2.5)",
        "desc": "CO Oxidation. Standard: CuO-CeO2."
    },
    "Nitrogen (N2)": {
        "bond": 1.09, "target_site": 2.480, "ref": "Fe (Harmonic 2.25)",
        "desc": "Ammonia Synthesis. Standard: Fe-K."
    },
    "Methane (CH4)": {
        "bond": 1.09, "target_site": 2.720, "ref": "Rh (Harmonic 2.5)",
        "desc": "C-H Activation. Standard: Rh."
    },
    "CO2 (Reduction)": {
        "bond": 1.16, "target_site": 2.610, "ref": "Cu/Au boundary",
        "desc": "CO2 to Fuels."
    },
    "NOx (Reduction)": {
        "bond": 1.15, "target_site": 2.580, "ref": "Rh",
        "desc": "Catalytic Converter."
    }
}

# --- HELPER FUNCTIONS ---
def get_site_distance(row):
    a = row['a_angstrom']
    struct = row['structure']
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

def check_chemical_risks(components, target_name):
    """
    Returns a list of warning tags based on chemical reality.
    But does NOT affect the Score.
    """
    tags = []
    
    elems = [c['element'] for c in components]
    roles = [c['role'] for c in components]
    vecs  = [c['vec'] for c in components]
    
    # 1. EXPLOSIVE RISK (Carbides of Group 11)
    if 'C' in elems:
        if 'Ag' in elems or 'Au' in elems or 'Cu' in elems:
            tags.append("☢️ EXPLOSIVE")
    
    # 2. INERTNESS RISK (Full d-shell trying to break strong bonds)
    # Target N2 or CH4 (Hard bonds) using Noble/Coinage metals (VEC > 10)
    if target_name in ["Nitrogen (N2)", "Methane (CH4)"]:
        # If Base is Au/Ag/Cu and no strong activator (like Fe, Ru, Os)
        base_vec = components[0]['vec'] # Assume first is base
        if base_vec >= 10.5: 
             tags.append("❄️ INERT")

    # 3. POISONING RISK (Oxide Armor)
    if 'Armor' in roles:
        tags.append("🛡️ OXIDE")
        
    # 4. STABILITY RISK (Soft metals)
    if 'Soft' in roles:
        tags.append("💧 SOFT")
        
    # 5. COST RISK
    costs = [c['cost_index'] for c in components]
    if max(costs) > 100:
        tags.append("💰 $$$")

    return " ".join(tags)

def solve_alloy(components, ratios, target_site, target_name):
    # Geometry Mix
    mix_site = sum([c['site_dist'] * r for c, r in zip(components, ratios)])
    # VEC Mix
    mix_vec = sum([c['vec'] * r for c, r in zip(components, ratios)])
    # Cost Mix
    mix_cost = sum([c['cost_index'] * r for c, r in zip(components, ratios)])
    
    name_parts = [f"{c['element']}{int(r*100)}" for c, r in zip(components, ratios)]
    alloy_name = "-".join(name_parts)
    
    # SCORING (PURE GEOMETRY)
    dev = abs(mix_site - target_site)
    geo_score = np.exp(-30 * dev) * 100
    
    # We remove the VEC penalty to show "Pure Potential".
    # Instead, we just show VEC.
    final_score = geo_score 
    
    # RISKS
    risks = check_chemical_risks(components, target_name)
    
    return {
        "Alloy": alloy_name,
        "Site (A)": round(mix_site, 4),
        "VEC": round(mix_vec, 2),
        "Score": round(final_score, 1),
        "Risks": risks,
        "Components": [c['element'] for c in components]
    }

# --- UI ---
st.set_page_config(page_title="Trilex Oracle v7 (Unchained)", layout="wide", page_icon="⚡")

st.title("⚡ Trilex Oracle v7.0: Unchained")
st.markdown("**Philosophy:** Geometric Resonance is the Law. Chemistry is just a constraint.")

df = load_data()
if df.empty: st.stop()

# CONFIG
col1, col2 = st.columns([1, 2])
with col1:
    mode = st.radio("Search Mode:", ["Pure Elements", "Binary Alloys", "Ternary Alloys"])
    
with col2:
    target_name = st.selectbox("Target Reaction:", list(MOLECULES.keys()))
    t_data = MOLECULES[target_name]
    st.info(f"**Target:** {t_data['target_site']} Å | {t_data['desc']}")

# RUN
if st.button("SCAN UNIVERSE"):
    results = []
    metal_list = df.to_dict('records')
    
    # Progress
    progress_bar = st.progress(0)
    
    if mode == "Pure Elements":
        for m in metal_list:
            results.append(solve_alloy([m], [1.0], t_data['target_site'], target_name))
        progress_bar.progress(100)
            
    elif mode == "Binary Alloys":
        # Smart Filter: Only use 'Base' or 'Noble' as primary component to save time
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        others = metal_list
        total = len(bases)
        
        for i, b in enumerate(bases):
            for o in others:
                if b['element'] == o['element']: continue
                # Ratios: 50/50, 80/20
                for r in [0.5, 0.8]:
                    results.append(solve_alloy([b, o], [r, 1-r], t_data['target_site'], target_name))
            progress_bar.progress((i+1)/total)
            
    elif mode == "Ternary Alloys":
        # Base + Mod + Mod
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        modifiers = [m for m in metal_list if m['role'] != 'Soft'] # Exclude soft from ternary modifiers to speed up?
        # Actually, let's include all but limit combinations
        modifiers = metal_list[:25] # Limit search space for demo speed
        
        total = len(bases)
        for i, b in enumerate(bases):
            for m1, m2 in itertools.combinations(modifiers, 2):
                # Standard Doping
                results.append(solve_alloy([b, m1, m2], [0.7, 0.2, 0.1], t_data['target_site'], target_name))
            progress_bar.progress((i+1)/total)

    progress_bar.empty()
    
    # RESULTS
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(50)
        
        # Winner
        top = res_df.iloc[0]
        st.success(f"🏆 Geometric Champion: **{top['Alloy']}** (Score: {top['Score']})")
        if top['Risks']:
            st.warning(f"⚠️ Reality Check: {top['Risks']}")
        
        # Table
        st.dataframe(
            res_df[['Alloy', 'Score', 'Site (A)', 'VEC', 'Risks']], 
            use_container_width=True,
            column_config={
                "Score": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
                "Risks": st.column_config.TextColumn("Hazards")
            }
        )
    else:
        st.error("No results.")
