import streamlit as st
import pandas as pd
import numpy as np

# =====================================================================
# SIMUREALITY: METABOLISM TABLE GENERATOR
# =====================================================================

st.set_page_config(page_title="Simureality OS | Metabolism Generator", layout="wide", page_icon="🧬")

# --- ONTOLOGICAL CONSTANTS (FROM FUSION APP) ---
MASS_P = 938.272
MASS_N = 939.565
E_ELECTRON = 0.511
E_ALPHA = 28.32        
E_MACRO_LINK = 2.425   
E_LINK = 2.36          
E_PAIR = 1.18          
JITTER_COST = 0.0131   
E_SKIN_LINK = 1.35        
TENSION_PENALTY = 0.95   
E_MAGIC = 2.15           
MAGIC_NUMBERS = {2, 8, 20, 28, 50, 82, 126} 

# Топ стабильных макро-узлов для молекулярной сборки
STABLE_ISOTOPES = [
    (1, 1, 'H'), (6, 6, 'C'), (7, 7, 'N'), (8, 8, 'O'), 
    (9, 10, 'F'), (14, 14, 'Si'), (15, 16, 'P'), (16, 16, 'S'), 
    (17, 18, 'Cl'), (35, 44, 'Br'), (53, 74, 'I')
]

class SimurealityMacroCore:
    def __init__(self):
        self._macro_link_cache = {0: 0, 1: 0, 2: 1, 3: 3, 4: 6}

    def get_fcc_neighbors(self, node):
        x, y, z = node
        deltas = [(1,1,0), (1,-1,0), (-1,1,0), (-1,-1,0),
                  (1,0,1), (1,0,-1), (-1,0,1), (-1,0,-1),
                  (0,1,1), (0,1,-1), (0,-1,1), (0,-1,-1)]
        return [(x+dx, y+dy, z+dz) for dx, dy, dz in deltas]

    def compile_3d_crystal(self, n_clusters):
        if n_clusters in self._macro_link_cache: return self._macro_link_cache[n_clusters]
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
            for cand in candidates:
                bonds = sum(1 for n in self.get_fcc_neighbors(cand) if n in occupied)
                dist_sq = (cand[0]-cm_x)**2 + (cand[1]-cm_y)**2 + (cand[2]-cm_z)**2
                if bonds > max_bonds or (bonds == max_bonds and dist_sq < min_dist):
                    max_bonds, min_dist, best_pos = bonds, dist_sq, cand
            occupied.add(best_pos)
        total_macro_links = sum(sum(1 for n in self.get_fcc_neighbors(node) if n in occupied) for node in occupied) // 2
        self._macro_link_cache[n_clusters] = total_macro_links
        return total_macro_links

    def analyze_node_metabolism(self, Z, N):
        """Возвращает полный профиль ядра для Ассемблера"""
        n_alphas = min(Z // 2, N // 2)
        binding_alphas = n_alphas * E_ALPHA
        macro_links = self.compile_3d_crystal(n_alphas)
        binding_macro = macro_links * E_MACRO_LINK

        tension_penalty, surface_ports = 0.0, 0.0
        if macro_links > 10: tension_penalty = (macro_links - 10) * TENSION_PENALTY
        if n_alphas > 0:
            surface_ports = (n_alphas ** (2/3)) * 6.5
            if n_alphas > 25: 
                tension_penalty *= 0.65       
                surface_ports *= 1.15         
            surface_ports = int(surface_ports)

        magic_profit = 0
        if Z in MAGIC_NUMBERS: magic_profit += E_MAGIC
        if N in MAGIC_NUMBERS: magic_profit += E_MAGIC

        rem_Z = Z - (n_alphas * 2)
        rem_N = N - (n_alphas * 2)
        halo_total = rem_Z + rem_N
        binding_halo, jitter = 0.0, 0.0
        
        if n_alphas == 0:
            if Z == 1:
                if N == 1: binding_halo = 2.225         
                elif N >= 2: binding_halo = 8.482       
        else:
            pairs = halo_total // 2
            unpaired = halo_total % 2
            binding_halo += pairs * E_PAIR
            connected_halo = min(halo_total, surface_ports)
            binding_halo += connected_halo * E_SKIN_LINK
            
            if connected_halo > 0 and tension_penalty > 0:
                coverage_ratio = connected_halo / surface_ports
                corset_relief = tension_penalty * (coverage_ratio * 0.85) 
                tension_penalty -= corset_relief
            
            if unpaired > 0: jitter += JITTER_COST * 10
            overflow = halo_total - surface_ports
            if overflow > 0: jitter += overflow * E_ELECTRON 

        total_binding = binding_alphas + binding_macro + binding_halo + magic_profit - tension_penalty - jitter
        raw_mass = (Z * MASS_P) + (N * MASS_N)
        base_lag = raw_mass - total_binding
        
        return {
            "base_lag": base_lag,
            "total_binding": total_binding,
            "internal_jitter": jitter + tension_penalty,
            "magic_profit": magic_profit
        }

def get_lone_pairs(Z):
    if Z in [9, 17, 35, 53]: return 3
    if Z in [8, 16, 34]: return 2
    if Z in [7, 15]: return 1
    return 0

# --- UI ---
st.title("🧬 Генератор Таблицы Метаболизма (Simureality V7 Init)")
st.markdown("Трансляция параметров 3D-ядер в термодинамические лимиты для молекулярной сборки.")

engine = SimurealityMacroCore()

if st.button("🚀 Сгенерировать Информационные Профили"):
    results = []
    
    for Z, N, symbol in STABLE_ISOTOPES:
        profile = engine.analyze_node_metabolism(Z, N)
        
        # 1. Base Lag (Масса покоя / Вычислительный долг узла)
        L_base = profile["base_lag"]
        
        # 2. Эффективность внутреннего метаболизма (Кэш)
        efficiency = profile["total_binding"] / (Z + N)
        
        # 3. Открытые порты (Lone Pairs) - источники эфирного джиттера
        lp = get_lone_pairs(Z)
        
        # 4. Критический Порог Энтропии (T_crit)
        # Чем выше эффективность ядра и чем меньше у него висячих портов/внутреннего джиттера, 
        # тем бОльшую температурную нагрузку оно может переварить до того, как его заставит слиться с другим атомом.
        structural_integrity = efficiency + (profile["magic_profit"] * 0.5)
        entropy_load = lp + profile["internal_jitter"] + 1.0 # +1.0 для исключения деления на 0
        
        # Калибровочный коэффициент для приведения к условной шкале
        T_crit = (structural_integrity ** 2) / entropy_load * 100 
        
        # Водород - уникальный случай (нет макро-ядра, голый порт)
        if Z == 1: T_crit = 50.0 

        results.append({
            "Z": Z,
            "Символ": symbol,
            "L_base (Вычислительный Долг, MeV)": round(L_base, 3),
            "Эффективность Ядра (Кэш)": round(efficiency, 3),
            "Открытые Порты (LP)": lp,
            "Внутренний Джиттер": round(profile["internal_jitter"], 3),
            "T_crit (Порог Активации/Температура)": round(T_crit, 2)
        })

    df_meta = pd.DataFrame(results)
    st.dataframe(df_meta, use_container_width=True)
    
    # Визуализация логики
    st.info("""
    **Архитектурный анализ:**
    * **Кислород (O):** Имеет идеальное Магическое Ядро (Z=8, N=8). Его внутренний джиттер равен 0. Эффективность максимальна. $T_{crit}$ высокий. Кислород стабилен в одиночестве при низких $T$.
    * **Фтор (F):** Нет магической симметрии, 3 открытых порта. Энтропийная нагрузка огромна. $T_{crit}$ низкий. Фтор принудительно ищет слияния (реакции) даже в "холодном" вакууме.
    """)
    
    csv_data = df_meta.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Экспорт simureality_metabolism.csv", data=csv_data, file_name="simureality_metabolism.csv", mime="text/csv")
