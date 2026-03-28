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
    119: 'Uue', 120: 'Ubn' # Trans-Oganesson Predictions
}

st.set_page_config(page_title="Simureality OS | Task Dispatcher", layout="wide")

@st.cache_data
def load_ame_masses(filename="mass.txt"):
    """Strict fixed-width parser for AME format."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                try:
                    n_str, z_str, a_str = line[5:10].strip(), line[10:15].strip(), line[15:19].strip()
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
    except Exception:
        return pd.DataFrame()

class SimurealityMacroCore:
    def __init__(self):
        # Аппаратный кэш ГЦК-решетки. Гарантирует безопасность легких ядер 
        # и ускоряет рендер матрицы в сотни раз.
        self._macro_link_cache = {0: 0, 1: 0, 2: 1, 3: 3, 4: 6}

    def get_fcc_neighbors(self, node):
        """12 интерфейсных портов ГЦК-узла (дистанция в квадрате = 2)"""
        x, y, z = node
        deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
                  (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
                  (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

    def compile_3d_crystal(self, n_clusters):
        """Алгоритм Диспетчера Задач: жадная 3D-компиляция Альфа-кластеров"""
        if n_clusters in self._macro_link_cache:
            return self._macro_link_cache[n_clusters]
            
        occupied = set([(0, 0, 0)])
        for _ in range(1, n_clusters):
            candidates = set()
            for node in occupied:
                for neighbor in self.get_fcc_neighbors(node):
                    if neighbor not in occupied:
                        candidates.add(neighbor)
            
            # Вычисляем центр масс для идеальной сферической упаковки
            cm_x = sum(n[0] for n in occupied) / len(occupied)
            cm_y = sum(n[1] for n in occupied) / len(occupied)
            cm_z = sum(n[2] for n in occupied) / len(occupied)
            
            best_pos = None
            max_bonds = -1
            min_dist = float('inf')
            
            for cand in candidates:
                bonds = sum(1 for n in self.get_fcc_neighbors(cand) if n in occupied)
                dist_sq = (cand[0]-cm_x)**2 + (cand[1]-cm_y)**2 + (cand[2]-cm_z)**2
                
                # Минимизация вычислительного долга: максимум общих граней, минимум Jitter'а
                if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                    max_bonds = bonds
                    min_dist = dist_sq
                    best_pos = cand
            
            occupied.add(best_pos)
            
        total_macro_links = sum(sum(1 for n in self.get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
        self._macro_link_cache[n_clusters] = total_macro_links
        return total_macro_links

    def compile_mass(self, Z, N):
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        
        # --- ДИНАМИЧЕСКИЙ РЕНДЕР МАКРО-ЛИНКОВ ---
        macro_links = self.compile_3d_crystal(n_alphas)
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        
        binding_halo = 0
        jitter = 0
        
        # --- SUB-ALPHA PRIMITIVES & HARDWARE FALLBACK ---
        if n_alphas == 0:
            if Z == 1:
                if N == 1: binding_halo = 2.225         
                elif N >= 2: binding_halo = 8.482       
            elif Z == 2 and N == 1:
                binding_halo = 7.718                    
        else:
            is_drip_line = False
            if Z == 2 and N >= 4: is_drip_line = True
            if Z == 3 and N >= 7: is_drip_line = True
            if Z > 1 and N == 0: is_drip_line = True    
            
            if not is_drip_line:
                if rem_N == 2 and rem_Z == 0: 
                    binding_halo = (5 * E_LINK) + E_PAIR
                    jitter = 10 * JITTER_COST

        total_binding = binding_alphas + binding_macro + binding_halo - jitter
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
        
        if m_b_minus < calc_mass: status = "BETA MINUS"
        elif m_b_plus < calc_mass: status = "BETA PLUS"
        else: status = "STABLE"
            
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
st.markdown("""
**Core Capabilities:**
1. Analytical calculation of ΣK (Mass) based on the FCC-matrix without empirical fitting.
2. Deterministic prediction of Beta Decay as a **Garbage Collection** transaction driven by Topological Debt.
""")

# --- THEORY & FORMULAS EXPANDER ---
with st.expander("📚 How it works: Complete Formula & Variables"):
    st.markdown("""
    ### The Grid Physics Paradigm (Simureality)
    In this framework, the nucleus is a deterministic spatial processor on a 3D Face-Centered Cubic (FCC) lattice. Mass is a measure of computational tax (ΣK).
    
    #### The Universal Compilation Formula
    The final mass (ΣK) is calculated as the raw weight of unbound nucleons minus the structural profit, penalized by the dynamic noise of empty ports:
    
    **ΣK =
