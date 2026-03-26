import streamlit as st
import pandas as pd
import numpy as np

# --- SIMUREALITY ONTOLOGICAL CONSTANTS ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.295       # Hardware cache (Tetrahedron 2P+2N)
E_MACRO_LINK = 2.425   # Link between Alpha-clusters
E_LINK = 2.36          # Link for halo nucleons
E_PAIR = 1.18          # Instancing pairing bonus
JITTER_COST = 0.0131   # Empty port ping cost

# --- ELEMENT DICTIONARY (Z to Symbol) ---
ELEMENTS = {
    0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm',
    101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
    110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'
}

st.set_page_config(page_title="Simureality OS | Task Dispatcher", layout="wide")

@st.cache_data
def load_ame_masses(filename="mass.txt"):
    """Strict fixed-width parser for AME format."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line:
                    continue
                try:
                    n_str = line[5:10].strip()
                    z_str = line[10:15].strip()
                    a_str = line[15:19].strip()
                    be_str = line[54:65].strip().replace('#', '').replace('*', '')
                    
                    if not n_str or not z_str or not be_str: continue
                        
                    N, Z, A = int(n_str), int(z_str), int(a_str)
                    be_per_A_keV = float(be_str)
                    
                    total_be_MeV = (be_per_A_keV * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError:
                    continue
                    
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception as e:
        return pd.DataFrame()

class SimurealityMacroCore:
    def compile_mass(self, Z, N):
        """Analytical macro-architecture checksum calculation."""
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        # Macro-links heuristic for light nuclei
        macro_links = 0
        if n_alphas == 3: macro_links = 3 
        elif n_alphas == 4: macro_links = 6 
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        
        binding_halo = 0
        jitter = 0
        
        if rem_N == 2 and rem_Z == 0: 
            binding_halo = (5 * E_LINK) + E_PAIR
            jitter = 10 * JITTER_COST

        total_binding = binding_alphas + binding_macro + binding_halo - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

@st.cache_data
def generate_global_matrix(_engine, df_ame):
    """Batch analysis of all isotopes."""
    results = []
    for (Z, N), row in df_ame.iterrows():
        exp_mass = row['Mass_MeV']
        calc_mass = _engine.compile_mass(Z, N)
        delta = calc_mass - exp_mass
        
        # Decay vectors
        m_b_minus = _engine.compile_mass(Z + 1, N - 1) + E_ELECTRON
        m_b_plus = _engine.compile_mass(Z - 1, N + 1) + E_ELECTRON
        
        if m_b_minus < calc_mass:
            status = "BETA MINUS"
        elif m_b_plus < calc_mass:
            status = "BETA PLUS"
        else:
            status = "STABLE"
            
        sym = ELEMENTS.get(Z, "?")
        results.append({
            "Element": f"{sym}-{Z+N}",
            "Z": Z, "N": N, "A": Z+N,
            "AME (MeV)": round(exp_mass, 3),
            "Simureality (MeV)": round(calc_mass, 3),
            "Delta (MeV)": round(delta, 3),
            "Dispatcher Decision": status
        })
    
    return pd.DataFrame(results).sort_values(by=["Z", "N"])

# --- UI RENDERING ---
st.title("Simureality OS: Nuclear Task Dispatcher")
st.markdown("Analytical calculation of ΣK based on FCC-matrix without empirical fitting.")

df_masses = load_ame_masses("mass.txt")
engine = SimurealityMacroCore()

# Sidebar: Target Input
st.sidebar.header("Target Configuration")
target_Z = st.sidebar.number_input("Protons (Z)", min_value=0, max_value=118, value=6, step=1)
target_N = st.sidebar.number_input("Neutrons (N)", min_value=0, max_value=177, value=8, step=1)

# Dynamic Element Name Resolution
symbol = ELEMENTS.get(target_Z, "Unknown")
target_A = target_Z + target_N
st.sidebar.markdown(f"### Selected Isotope: **{symbol}-{target_A}**")

if df_masses.empty:
    st.sidebar.error("⚠️ Mass database not loaded. Check mass.txt")
else:
    st.sidebar.success(f"✅ Database loaded ({len(df_masses)} nuclei)")

st.write("---")
st.write("### Single Core Analysis")
col1, col2, col3 = st.columns(3)

calc_mass = engine.compile_mass(target_Z, target_N)
col1.metric(label="Simureality Mass (ΣK)", value=f"{calc_mass:.3f} MeV")

if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
    delta = calc_mass - exp_mass
    col2.metric(label="AME Reference (Experiment)", value=f"{exp_mass:.3f} MeV", delta=f"{delta:.3f} MeV (Delta)", delta_color="inverse")
else:
    col2.metric(label="AME Reference", value="No data")

mass_beta_minus = engine.compile_mass(target_Z + 1, target_N - 1) + E_ELECTRON
mass_beta_plus = engine.compile_mass(target_Z - 1, target_N + 1) + E_ELECTRON

if mass_beta_minus < calc_mass:
    profit = calc_mass - mass_beta_minus
    st.error(f"**FATAL DEBT.** BETA-MINUS DECAY triggered. Dropping an electron saves **{profit:.3f} MeV** of processing time.")
elif mass_beta_plus < calc_mass:
    profit = calc_mass - mass_beta_plus
    st.error(f"**FATAL DEBT.** BETA-PLUS DECAY triggered. Dropping a positron saves **{profit:.3f} MeV** of processing time.")
else:
    st.success("**[OK] Hardware assembly is stable.** Interface patches are mathematically unprofitable. ΣK is at global minimum.")

# --- GLOBAL LOG & STATISTICS ---
st.markdown("---")
st.write("### Global Compilation Log (AME2020 Matrix)")

if not df_masses.empty:
    with st.spinner('Synchronizing with database... Compiling matrix...'):
        global_df = generate_global_matrix(engine, df_masses)
        
        # Calculate Statistics
        global_df['Absolute Error (MeV)'] = global_df['Delta (MeV)'].abs()
        global_df['Error (%)'] = (global_df['Absolute Error (MeV)'] / global_df['AME (MeV)']) * 100
        
        max_err_mev = global_df['Absolute Error (MeV)'].max()
        mean_err_mev = global_df['Absolute Error (MeV)'].mean()
        overall_accuracy = 100.0 - global_df['Error (%)'].mean()
        
        # Display Stat Cards
        st.write("##### Aggregate Benchmark Metrics (MVP Core)")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(label="Overall Matrix Accuracy", value=f"{overall_accuracy:.4f} %")
        sc2.metric(label="Mean Delta (Error)", value=f"{mean_err_mev:.3f} MeV")
        sc3.metric(label="Max Delta (Heavy Nuclei Penalty)", value=f"{max_err_mev:.3f} MeV")
        
        st.dataframe(global_df.drop(columns=['Absolute Error (MeV)', 'Error (%)']), use_container_width=True, height=500)
        
        csv_data = global_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Matrix (CSV)", data=csv_data, file_name="simureality_global_log.csv", mime="text/csv")
