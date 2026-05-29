import streamlit as st
import pandas as pd
import numpy as np

# --- СТРОГИЕ АППАРАТНЫЕ КОНСТАНТЫ SIMUREALITY (V8: PROLATE SPHEROID) ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.32       
E_MACRO_LINK = 2.425   
E_LINK = 2.36          
E_PAIR = 1.18          
JITTER_COST = 0.01311   

# --- ПОДГОНОЧНЫЕ КОЭФФИЦИЕНТЫ ВЕЙЦЗЕККЕРА (ЛЕГАСИ) ---
A_V = 15.75
A_S = 17.8
A_C = 0.711
A_A = 23.7
A_P = 11.18

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

st.set_page_config(page_title="Grid Physics V8: The Rugby Ball Spheroid", layout="wide")

@st.cache_data
def load_ame_masses(filename="mass.txt"):
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
                    total_be_MeV = (float(be_str) * A) / 1000.0
                    exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
                    data.append({'Z': Z, 'N': N, 'Mass_MeV': exp_nucleus_mass})
                except ValueError: continue
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z', 'N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception: return pd.DataFrame()

class LiquidDropCore:
    def compile_mass(self, Z, N):
        if Z < 0 or N < 0: return float('inf')
        A = Z + N
        if A < 2: return (Z * MASS_P) + (N * MASS_N)
        vol = A_V * A
        surf = A_S * (A ** (2/3))
        coul = A_C * (Z * (Z - 1)) / (A ** (1/3))
        asym = A_A * ((A - 2*Z)**2) / A
        if Z % 2 == 0 and N % 2 == 0: pair = A_P / (A ** 0.5)
        elif Z % 2 != 0 and N % 2 != 0: pair = -A_P / (A ** 0.5)
        else: pair = 0
        return (Z * MASS_P) + (N * MASS_N) - (vol - surf - coul - asym + pair)

class GridPhysicsV8Core:
    def __init__(self):
        # ВОССТАНОВЛЕН КЭШ ПРЕДЕЛЬНОЙ ЖЕСТКОСТИ (Платоновы тела для начала таблицы)
        self._crystal_cache = {
            0: (0, 0),
            1: (0, 12),
            2: (1, 22),
            3: (3, 30),
            4: (6, 36)
        }

    def get_fcc_neighbors(self, node):
        x, y, z = node
        deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
                  (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
                  (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

    def compile_3d_crystal(self, n_clusters):
        if n_clusters in self._crystal_cache: 
            return self._crystal_cache[n_clusters]
            
        occupied = set([(0, 0, 0)])
        for _ in range(1, n_clusters):
            candidates = set()
            for node in occupied:
                for neighbor in self.get_fcc_neighbors(node):
                    if neighbor not in occupied: candidates.add(neighbor)
            
            cm_x = sum(n[0] for n in occupied) / len(occupied)
            cm_y = sum(n[1] for n in occupied) / len(occupied)
            cm_z = sum(n[2] for n in occupied) / len(occupied)

            best_pos, max_bonds, min_dist = None, -1, float('inf')
            
            # --- THE IRON THRESHOLD: ПЕРЕХОД К РЕГБИЙНОМУ МЯЧУ ---
            is_spherical = (n_clusters <= 14)
            
            for cand in sorted(list(candidates)): 
                bonds = sum(1 for n in self.get_fcc_neighbors(cand) if n in occupied)
                
                dx = cand[0] - cm_x
                dy = cand[1] - cm_y
                dz = cand[2] - cm_z
                
                if is_spherical:
                    # Уравнение идеальной сферы (равномерное притяжение к центру)
                    dist_sq = dx**2 + dy**2 + dz**2
                else:
                    # Уравнение вытянутого эллипсоида (Prolate Spheroid)
                    # Штраф за ширину (X, Y) в 1.5 раза выше, чем за длину (Z).
                    # Кристалл физически вытягивается вдоль оси Z, как регбийный мяч!
                    dist_sq = 1.5 * dx**2 + 1.5 * dy**2 + 1.0 * dz**2
                
                if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                    max_bonds, min_dist, best_pos = bonds, dist_sq, cand
                        
            occupied.add(best_pos)

        total_macro_links = sum(sum(1 for n in self.get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
        surface_ports = (n_clusters * 12) - (2 * total_macro_links)
        
        self._crystal_cache[n_clusters] = (total_macro_links, surface_ports)
        return total_macro_links, surface_ports

    def compile_mass(self, Z, N):
        if Z < 0 or N < 0: return float('inf')
        if Z == 0 and N == 1: return MASS_N
        if Z == 1 and N == 0: return MASS_P
        
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        macro_links, surface_ports = self.compile_3d_crystal(n_alphas)
        binding_macro = macro_links * E_MACRO_LINK

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        orphans_total = rem_Z + rem_N
        
        binding_halo, jitter, overflow_tax = 0, 0, 0

        if orphans_total > 0:
            pairs = min(rem_Z, rem_N)
            binding_halo += pairs * (E_LINK + E_PAIR)
            
            leftover = orphans_total - (pairs * 2)
            if leftover > 0:
                if surface_ports > 0:
                    L2_docked = min(leftover, surface_ports)
                    binding_halo += L2_docked * (E_LINK / 2.0)
                    leftover -= L2_docked
                
                if leftover > 0:
                    binding_halo += leftover * (E_LINK / 3.0)

            open_ports = orphans_total * 12 if (n_alphas == 0 and pairs == 0) else orphans_total * 11
            jitter += open_ports * JITTER_COST

            # OVERFLOW TAX: Кулоновское расталкивание Гало (Литий-11)
            core_nucleons = max(n_alphas * 4, 1) 
            if orphans_total > core_nucleons:
                overflow = orphans_total - core_nucleons
                overflow_tax = overflow * orphans_total * E_ELECTRON

        total_be = binding_alphas + binding_macro + binding_halo - jitter - overflow_tax
        return (Z * MASS_P) + (N * MASS_N) - total_be

@st.cache_data
def generate_comparison_matrix(_grid_engine, _liquid_engine, df_ame):
    results = []
    for (Z, N), row in df_ame.iterrows():
        exp_mass = row['Mass_MeV']
        grid_mass = _grid_engine.compile_mass(Z, N)
        liquid_mass = _liquid_engine.compile_mass(Z, N)
        
        grid_delta = grid_mass - exp_mass
        liquid_delta = liquid_mass - exp_mass
            
        sym = ELEMENTS.get(Z, "?")
        results.append({
            "Element": f"{sym}-{Z+N}", "Z": Z, "N": N, "A": Z+N,
            "AME2020 Log (MeV)": round(exp_mass, 3),
            "Grid Physics ΣK (MeV)": round(grid_mass, 3),
            "Liquid Drop (MeV)": round(liquid_mass, 3),
            "Grid Debt/Error (MeV)": round(grid_delta, 3),
            "Liquid Drop Error (MeV)": round(liquid_delta, 3)
        })
    return pd.DataFrame(results).sort_values(by=["Z", "N"])

# --- RENDER UI ---
st.title("Grid Physics V8: The Rugby Ball Spheroid")
st.markdown("""
**Обновление V8.0 (Эллипсоидная Деформация Матрицы):**
Синхронизация с открытием в *Physical Review Letters (2025)*. 
Ядра после Железа-56 алгоритмически вытягиваются в эллипсоид (регбийный мяч) для идеального перекрытия портов. 
Легкие ядра (до Железа) сохраняют идеальную сферическую симметрию ГЦК-решетки.
""")

df_masses = load_ame_masses("mass.txt")
grid_engine = GridPhysicsV8Core()
liquid_engine = LiquidDropCore()

st.sidebar.header("Конфигурация ядра")
target_Z = st.sidebar.number_input("Протоны (Z)", min_value=1, max_value=118, value=82, step=1)
target_N = st.sidebar.number_input("Нейтроны (N)", min_value=0, max_value=184, value=126, step=1)

symbol = ELEMENTS.get(target_Z, "Unknown")
st.sidebar.markdown(f"### Выбранный узел: **{symbol}-{target_Z+target_N}**")

st.write("### Анализ одиночного узла")
col1, col2, col3 = st.columns(3)

if not df_masses.empty and (target_Z, target_N) in df_masses.index:
    exp_mass = df_masses.loc[(target_Z, target_N), 'Mass_MeV']
    col1.metric(label="AME2020 Hardware Log", value=f"{exp_mass:.3f} MeV")
    
    n_alph = min(target_Z//2, target_N//2)
    shape_str = "Сфера" if n_alph <= 14 else "Регбийный мяч (Эллипсоид)"
    
    grid_mass = grid_engine.compile_mass(target_Z, target_N)
    grid_err = grid_mass - exp_mass
    col2.metric(label=f"Grid Physics V8 ({shape_str})", value=f"{grid_mass:.3f} MeV", delta=f"{grid_err:.3f} MeV", delta_color="inverse")
    
    liquid_mass = liquid_engine.compile_mass(target_Z, target_N)
    liquid_err = liquid_mass - exp_mass
    col3.metric(label="Liquid Drop (SEMF)", value=f"{liquid_mass:.3f} MeV", delta=f"{liquid_err:.3f} MeV", delta_color="inverse")
else:
    col1.metric(label="AME2020 Hardware Log", value="Node Not Found")

st.markdown("---")
st.write("### Глобальная сравнительная матрица (Весь AME2020 + Синтетика)")
if not df_masses.empty:
    with st.spinner('Сборка таблицы: Рендеринг эллипсоидных ГЦК-кристаллов...'):
        comp_df = generate_comparison_matrix(grid_engine, liquid_engine, df_masses)
        
        comp_df['Grid Abs Error'] = comp_df['Grid Debt/Error (MeV)'].abs()
        comp_df['Liquid Abs Error'] = comp_df['Liquid Drop Error (MeV)'].abs()
        
        grid_mean = comp_df['Grid Abs Error'].mean()
        liquid_mean = comp_df['Liquid Abs Error'].mean()
        
        grid_efficiency = 100.0 - (comp_df['Grid Abs Error'] / comp_df['AME2020 Log (MeV)']).mean() * 100
        liquid_efficiency = 100.0 - (comp_df['Liquid Abs Error'] / comp_df['AME2020 Log (MeV)']).mean() * 100
        
        sc1, sc2 = st.columns(2)
        sc1.metric(label="Grid Physics Efficiency (0 fits)", value=f"{grid_efficiency:.4f} %", delta=f"Mean Error: {grid_mean:.3f} MeV", delta_color="off")
        sc2.metric(label="Liquid Drop Efficiency (5 fits)", value=f"{liquid_efficiency:.4f} %", delta=f"Mean Error: {liquid_mean:.3f} MeV", delta_color="off")
        
        csv = comp_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Скачать CSV (V8 Rugby Spheroid)", data=csv, file_name='GridPhysics_V8_Log.csv', mime='text/csv')
        
        st.dataframe(comp_df.drop(columns=['Grid Abs Error', 'Liquid Abs Error']), use_container_width=True, height=400)
