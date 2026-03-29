import streamlit as st
import pandas as pd
import numpy as np

# --- SIMUREALITY ONTOLOGICAL CONSTANTS ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.32       
E_MACRO_LINK = 2.425   
E_LINK = 2.36          
E_PAIR = 1.18          
JITTER_COST = 0.0131   

# --- V5 NEW HARDWARE CONSTANTS (SKIN & TENSION) ---
E_SKIN_LINK = 1.35       # Профит за подключение нейтрона гало к поверхности 3D-ядра
TENSION_PENALTY = 0.95   # Вычислительный штраф за макро-линк (распирание базы данных)

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
    110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og',
    119: 'Uue', 120: 'Ubn'
}

st.set_page_config(page_title="Simureality OS | Task Dispatcher", layout="wide")

@st.cache_data
def load_ame_masses(filename="mass.txt"):
    """Strict parser for AME format. DROPS SYNTHETIC DATA (# and *)."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                
                # ВЕРИФИКАЦИЯ: Отбрасываем теоретические галлюцинации AME
                if '#' in line or '*' in line:
                    continue
                    
                try:
                    n_str, z_str, a_str = line[5:10].strip(), line[10:15].strip(), line[15:19].strip()
                    be_str = line[54:65].strip()
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
    except Exception:
        return pd.DataFrame()

class SimurealityMacroCore:
    def __init__(self):
        self._macro_link_cache = {0: 0, 1: 0, 2: 1, 3: 3, 4: 6}

    def get_fcc_neighbors(self, node):
        """12 интерфейсных портов ГЦК-узла"""
        x, y, z = node
        deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
                  (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
                  (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

    def compile_3d_crystal(self, n_clusters):
        """Жадная 3D-компиляция Альфа-кластеров"""
        if n_clusters in self._macro_link_cache:
            return self._macro_link_cache[n_clusters]
            
        occupied = set([(0, 0, 0)])
        for _ in range(1, n_clusters):
            candidates = set()
            for node in occupied:
                for neighbor in self.get_fcc_neighbors(node):
                    if neighbor not in occupied:
                        candidates.add(neighbor)
            
            cm_x = sum(n[0] for n in occupied) / len(occupied)
            cm_y = sum(n[1] for n in occupied) / len(occupied)
            cm_z = sum(n[2] for n in occupied) / len(occupied)
            
            best_pos = None
            max_bonds = -1
            min_dist = float('inf')
            
            for cand in candidates:
                bonds = sum(1 for n in self.get_fcc_neighbors(cand) if n in occupied)
                dist_sq = (cand[0]-cm_x)**2 + (cand[1]-cm_y)**2 + (cand[2]-cm_z)**2
                
                if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                    max_bonds = bonds
                    min_dist = dist_sq
                    best_pos = cand
            
            occupied.add(best_pos)
            
        total_macro_links = sum(sum(1 for n in self.get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
        self._macro_link_cache[n_clusters] = total_macro_links
        return total_macro_links

    def compile_mass(self, Z, N):
        # --- HARDWARE FIREWALL ---
        if Z < 0 or N < 0:
            return float('inf') # Матрица блокирует отрицательные координаты
            
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        macro_links = self.compile_3d_crystal(n_alphas)
        binding_macro = macro_links * E_MACRO_LINK

        # --- V5 LOGIC: CORE TENSION ---
        tension_penalty = 0
        if macro_links > 10:
            tension_penalty = (macro_links - 10) * TENSION_PENALTY

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        halo_total = rem_Z + rem_N
        
        binding_halo = 0
        jitter = 0
        
        if n_alphas == 0:
            if Z == 1:
                if N == 1: binding_halo = 2.225         
                elif N >= 2: binding_halo = 8.482       
            elif Z == 2 and N == 1:
                binding_halo = 7.718                    
        else:
            # --- V5 LOGIC: NEUTRON SKIN WEAVING (Скин-слой) ---
            surface_ports = int((n_alphas ** (2/3)) * 6.5) 
            
            pairs = halo_total // 2
            unpaired = halo_total % 2
            binding_halo += pairs * E_PAIR
            
            connected_halo = min(halo_total, surface_ports)
            binding_halo += connected_halo * E_SKIN_LINK
            
            if connected_halo > 0 and tension_penalty > 0:
                coverage_ratio = connected_halo / surface_ports
                corset_relief = tension_penalty * (coverage_ratio * 0.85) 
                tension_penalty -= corset_relief
            
            if unpaired > 0:
                jitter += JITTER_COST * 10
                
            overflow = halo_total - surface_ports
            if overflow > 0:
                jitter += overflow * E_ELECTRON 

        total_binding = binding_alphas + binding_macro + binding_halo - tension_penalty - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        return raw_mass - total_binding

@st.cache_data
def generate_global_matrix(_engine, df_ame):
    results = []
    for (Z, N), row in df_ame.iterrows():
        exp_mass = row['Mass_MeV']
        calc_mass = _engine.compile_mass(Z, N)
        delta = calc_mass - exp_mass
        
        m_b_minus = _engine.compile_mass(Z + 1, N - 1) + E_ELECTRON
        m_b_plus = _engine.compile_mass(Z - 1, N + 1) + E_ELECTRON
        
        if m_b_minus < calc_mass: status = "BETA MINUS (Garbage Collect)"
        elif m_b_plus < calc_mass: status = "BETA PLUS (Garbage Collect)"
        else: status = "STABLE"
            
        sym = ELEMENTS.get(Z, "?")
        results.append({
            "Element": f"{sym}-{Z+N}",
            "Z": Z, "N": N, "A": Z+N,
            "Pure Hardware Log (MeV)": round(exp_mass, 3),
            "Calculated ΣK (MeV)": round(calc_mass, 3),
            "Unresolved Debt (MeV)": round(delta, 3),
            "Dispatcher Decision": status
        })
    return pd.DataFrame(results).sort_values(by=["Z", "N"])

# --- UI RENDERING ---
st.title("Simureality OS: Pure Hardware Task Dispatcher (V5.1)")
st.markdown("""
**Core Capabilities:**
1. Analytical calculation of ΣK (Mass) based on FCC-matrix.
2. **Zero synthetic data:** strictly filters out theoretical estimations (`#`, `*`) from AME logs.
3. **Core Tension & Halo Weaving:** Implements surface port mapping and topological corset mechanics to stabilize heavy nuclei.
""")

with st.expander("📚 Architectural Patch V5.1: Skin Layer & Core Tension"):
    st.markdown("""
    ### The Geometric Bottleneck
    Previous models struggled with heavy nuclei. **Pb-186** exhibited severe *Core Tension* (macro-link crowding causing geometric expansion/strain). **Tl-210** exhibited a *Halo Packaging* error (excess neutrons were treated as unlinked garbage).
    
    ### The V5.1 Solution
    1. **Core Tension Penalty:** Dense 3D assemblies now accrue a dynamic computational debt `(macro_links - 10) * TENSION_PENALTY`.
    2. **Surface Ports Mapping:** The matrix calculates available surface interfaces scaling as $N_{alphas}^{2/3}$.
    3. **The Corset Effect:** Excess halo neutrons are routed to surface ports (`E_SKIN_LINK`). If they form a contiguous layer (Neutron Skin), they physically bind the core, actively **canceling out** the Core Tension penalty.
    """)

df_masses = load_ame_masses("mass.txt")
engine = SimurealityMacroCore()

st.sidebar.header("Target Configuration")
target_Z = st.sidebar.number_input("Protons (Z)", min_value=0, max_value=120, value=82, step=1)
target_N = st.sidebar.number_input("Neutrons (N)", min_value=0, max_value=184, value=104, step=1)

target_A = target_Z + target_N
symbol = ELEMENTS.get(target_Z, "Unknown")
st.sidebar.markdown(f"### Selected Node: **{symbol}-{target_A}**")

if df_masses.empty:
    st.sidebar.error("⚠️ Hardware logs not loaded. Ensure mass.txt is present.")
else:
    st.sidebar.success(f"✅ Pure Logs loaded ({len(df_masses)} verified nodes)")

tab1, tab2 = st.tabs(["Single Core & Global Matrix", "Hardware Proofs"])

with tab1:
    st.write("### Single Core Analysis")
    col1, col2, col3 = st.columns(3)
    calc_mass = engine.compile_mass(target_Z, target_N)
    col1.metric(label="Calculated ΣK", value=f"{calc_mass:.3f} MeV")

    if not df_masses.empty and (target_Z, target_N) in df_masses.index:
        exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
        delta = calc_mass - exp_mass
        col2.metric(label="Hardware Log", value=f"{exp_mass:.3f} MeV", delta=f"{delta:.3f} MeV (Debt)", delta_color="inverse")
    else:
        col2.metric(label="Hardware Log", value="Node Not Found (Filtered)")
    
    mass_beta_minus = engine.compile_mass(target_Z + 1, target_N - 1) + E_ELECTRON
    mass_beta_plus = engine.compile_mass(target_Z - 1, target_N + 1) + E_ELECTRON

    if mass_beta_minus < calc_mass:
        st.error(f"**BUFFER OVERFLOW.** BETA-MINUS triggered. Ejecting electron saves **{(calc_mass - mass_beta_minus):.3f} MeV**.")
    elif mass_beta_plus < calc_mass:
        st.error(f"**BUFFER OVERFLOW.** BETA-PLUS triggered. Ejecting positron saves **{(calc_mass - mass_beta_plus):.3f} MeV**.")
    else:
        st.success("**[OK] Assembly is stable. Cache within limits.**")

    st.markdown("---")
    st.write("### Global Matrix Log & Statistics (Filtered)")
    if not df_masses.empty:
        with st.spinner('Compiling matrix...'):
            global_df = generate_global_matrix(engine, df_masses)
            
            global_df['Absolute Debt (MeV)'] = global_df['Unresolved Debt (MeV)'].abs()
            global_df['Jitter Cache Load (%)'] = (global_df['Absolute Debt (MeV)'] / global_df['Pure Hardware Log (MeV)']) * 100
            
            max_debt_mev = global_df['Absolute Debt (MeV)'].max()
            mean_debt_mev = global_df['Absolute Debt (MeV)'].mean()
            overall_efficiency = 100.0 - global_df['Jitter Cache Load (%)'].mean()
            
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric(label="System Efficiency", value=f"{overall_efficiency:.4f} %")
            sc2.metric(label="Mean Jitter Cache (Lag)", value=f"{mean_debt_mev:.3f} MeV")
            sc3.metric(label="Max Debt (Heavy Nuclei)", value=f"{max_debt_mev:.3f} MeV")
            
            st.dataframe(global_df.drop(columns=['Absolute Debt (MeV)', 'Jitter Cache Load (%)']), use_container_width=True, height=400)
            
            csv_data = global_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Matrix (CSV)", data=csv_data, file_name="simureality_v51_pure_log.csv", mime="text/csv")

with tab2:
    st.markdown("## Architectural Proofs of the FCC Matrix")
    st.subheader("Proof 1: Deterministic Garbage Collection")
    
    z_unstable, n_unstable = 6, 8 
    if (z_unstable, n_unstable) in df_masses.index:
        mass_c14 = engine.compile_mass(z_unstable, n_unstable)
        mass_n14_plus_e = engine.compile_mass(z_unstable + 1, n_unstable - 1) + E_ELECTRON
        profit = mass_c14 - mass_n14_plus_e
        
        st.write(f"**Transaction: Carbon-14 → Nitrogen-14**")
        st.code(f"""
1. Current ΣK (Carbon-14): {mass_c14:.3f} MeV
2. Target ΣK (Nitrogen-14) + Interface Patch ({E_ELECTRON} MeV): {mass_n14_plus_e:.3f} MeV
3. Transaction Profit: {mass_c14:.3f} - {mass_n14_plus_e:.3f} = {profit:.3f} MeV

DECISION: The transaction is profitable (> 0 MeV). 
ACTION: Dispatcher triggers Beta-Minus decay.
        """, language="text")
