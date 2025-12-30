import streamlit as st
import pandas as pd
import numpy as np
import itertools

# ==============================================================================
# TRILEX ORACLE v7.1: CONTROLLED CHAOS
# Features: Restored Filters, Risk Legend, Chemical Toggle
# ==============================================================================

# --- CORE PHYSICS ---
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

def get_risk_tags(components, target_name):
    tags = []
    elems = [c['element'] for c in components]
    roles = [c['role'] for c in components]
    
    # 1. EXPLOSIVE (Carbides of Group 11)
    if 'C' in elems and any(x in elems for x in ['Ag', 'Au', 'Cu']):
        tags.append("☢️")
    
    # 2. INERT (Noble metals vs Hard Bonds)
    if target_name in ["Nitrogen (N2)", "Methane (CH4)"]:
        base_vec = components[0]['vec']
        if base_vec >= 10.5 and 'Fe' not in elems and 'Ru' not in elems:
            tags.append("❄️")

    # 3. OXIDE ARMOR
    if 'Armor' in roles: tags.append("🛡️")
    
    # 4. SOFT/UNSTABLE
    if 'Soft' in roles: tags.append("💧")
    
    # 5. EXPENSIVE
    costs = [c['cost_index'] for c in components]
    if max(costs) > 100: tags.append("💰")
        
    return tags

def solve_alloy(components, ratios, target_site, target_name, ignore_risks):
    # Mix Properties
    mix_site = sum([c['site_dist'] * r for c, r in zip(components, ratios)])
    mix_vec = sum([c['vec'] * r for c, r in zip(components, ratios)])
    mix_cost = sum([c['cost_index'] * r for c, r in zip(components, ratios)])
    
    name_parts = [f"{c['element']}{int(r*100)}" for c, r in zip(components, ratios)]
    alloy_name = "-".join(name_parts)
    
    # SCORING
    dev = abs(mix_site - target_site)
    geo_score = np.exp(-30 * dev) * 100
    
    tags = get_risk_tags(components, target_name)
    
    # CHEMICAL PENALTY LOGIC
    penalty = 1.0
    if not ignore_risks:
        if "☢️" in tags: penalty *= 0.0  # Dead
        if "❄️" in tags: penalty *= 0.1  # Very weak
        if "💧" in tags: penalty *= 0.5  # Unstable
        
    final_score = geo_score * penalty
    
    return {
        "Alloy": alloy_name,
        "Site (A)": round(mix_site, 4),
        "VEC": round(mix_vec, 2),
        "Score": round(final_score, 1),
        "Hazards": " ".join(tags),
        "Components": [c['element'] for c in components]
    }

# --- UI ---
st.set_page_config(page_title="Trilex Oracle v7.1", layout="wide", page_icon="⚡")

st.title("⚡ Trilex Oracle v7.1")
st.markdown("**Simureality Engineering:** Geometric Resonance & Chemical Reality.")

df = load_data()
if df.empty: st.stop()

# --- SIDEBAR CONFIG ---
st.sidebar.header("1. Strategy")
mode = st.sidebar.radio("Search Mode:", ["Pure Elements", "Binary Alloys", "Ternary Alloys"])
target_name = st.sidebar.selectbox("Target Reaction:", list(MOLECULES.keys()))
t_data = MOLECULES[target_name]

st.sidebar.info(f"**Target:** {t_data['target_site']} Å\n\n{t_data['desc']}")

st.sidebar.header("2. Ingredients (Filters)")
col_f1, col_f2 = st.sidebar.columns(2)
with col_f1:
    allow_noble = st.checkbox("Noble (Pt, Au)", value=True)
    allow_armor = st.checkbox("Armor (Al, Ti)", value=True)
with col_f2:
    allow_soft = st.checkbox("Soft (Zn, Pb)", value=False)
    allow_dwarf = st.checkbox("Dwarfs (C, B)", value=True)

st.sidebar.header("3. Philosophy")
ignore_risks = st.sidebar.checkbox("Ignore Chemical Risks (Unchained Mode)", value=True, 
                                   help="If checked, shows purely geometric potential (Score 100) even if chemically unstable.")

# FILTER DATAFRAME
filtered_df = df.copy()
if not allow_noble: filtered_df = filtered_df[filtered_df['role'] != 'Noble']
if not allow_armor: filtered_df = filtered_df[filtered_df['role'] != 'Armor']
if not allow_soft: filtered_df = filtered_df[filtered_df['role'] != 'Soft']
if not allow_dwarf: filtered_df = filtered_df[filtered_df['role'] != 'Dwarf']

# LEGEND
with st.sidebar.expander("ℹ️ Legend & Risks"):
    st.markdown("""
    * ☢️ **Explosive:** Unstable Carbides/Compounds.
    * ❄️ **Inert:** Noble metal trying to break hard bond.
    * 🛡️ **Oxide:** Forms passivating layer (Al, Ti).
    * 💧 **Soft:** Low melting point, unstable surface.
    * 💰 **High Cost:** Contains Precious Metals.
    """)

st.metric("Materials in Mix", len(filtered_df))

# --- MAIN LOOP ---
if st.button("RUN SCAN"):
    results = []
    metal_list = filtered_df.to_dict('records')
    progress_bar = st.progress(0)
    
    # 1. PURE
    if mode == "Pure Elements":
        for m in metal_list:
            results.append(solve_alloy([m], [1.0], t_data['target_site'], target_name, ignore_risks))
        progress_bar.progress(100)
            
    # 2. BINARY
    elif mode == "Binary Alloys":
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        others = metal_list
        if not bases: bases = metal_list # Fallback
        
        total = len(bases)
        for i, b in enumerate(bases):
            for o in others:
                if b['element'] == o['element']: continue
                for r in [0.5, 0.8, 0.9]:
                    results.append(solve_alloy([b, o], [r, 1-r], t_data['target_site'], target_name, ignore_risks))
            progress_bar.progress((i+1)/total)
            
    # 3. TERNARY
    elif mode == "Ternary Alloys":
        bases = [m for m in metal_list if m['role'] in ['Base', 'Noble']]
        modifiers = [m for m in metal_list if m['role'] not in ['Base', 'Noble']]
        if len(modifiers) > 20: modifiers = modifiers[:20] # Optimization
        
        total = len(bases)
        for i, b in enumerate(bases):
            for m1, m2 in itertools.combinations(modifiers, 2):
                results.append(solve_alloy([b, m1, m2], [0.7, 0.2, 0.1], t_data['target_site'], target_name, ignore_risks))
            progress_bar.progress((i+1)/total)

    progress_bar.empty()
    
    # RESULTS
    if results:
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False).head(50)
        
        top = res_df.iloc[0]
        st.success(f"🏆 Champion: **{top['Alloy']}** (Score: {top['Score']})")
        if top['Hazards']: st.warning(f"Hazards: {top['Hazards']}")
        
        st.dataframe(
            res_df[['Alloy', 'Score', 'Site (A)', 'VEC', 'Hazards']], 
            use_container_width=True,
            column_config={
                "Score": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
            }
        )
    else:
        st.error("No matches. Check your filters.")
