import streamlit as st
import pandas as pd
import math
import os
import plotly.express as px

# ==========================================================================================
# SIMUREALITY: CHRONOS ENGINE V7.1 (BULLETPROOF EDITION)
# ==========================================================================================

st.set_page_config(page_title="Simureality Chronos", layout="wide")

class GridPhysicsEngine:
    def __init__(self):
        self.m_e = 0.511  
        self.PI = math.pi
        self.gamma_1D = 2.0 / math.sqrt(3.0)        
        self.gamma_vol = self.gamma_1D ** (1.0/3.0) 
        self.gamma_sys = 1.0418                     
        self.eta_fcc = self.PI / (3 * math.sqrt(2)) 
        self.E_link = 4 * self.m_e * self.gamma_1D  
        self.E_alpha = 12 * self.E_link             
        self.a_V = 6 * self.E_link * self.gamma_sys 
        self.a_S = 14.5                             
        self.a_C = self.eta_fcc / self.gamma_vol    
        self.a_Sym = 6 * self.E_link                
        self.delta = 12.0                           

    def geometric_shell_penalty(self, Z, N):
        shells = [2, 8, 20, 28, 50, 82, 126, 184]
        dist_Z = min([abs(Z - m) for m in shells])
        dist_N = min([abs(N - m) for m in shells])
        K_DEFORM = (4 * (1/137.036)) / (self.PI**2 * self.gamma_sys)
        if Z < 40: return 0
        return K_DEFORM * (dist_Z * dist_N) * (dist_Z + dist_N)**0.8

    def calculate_energy(self, Z, A):
        N = A - Z
        if Z <= 20:
            n_alpha = A // 4
            rem = A % 4
            links = 0 if n_alpha < 2 else 3 * n_alpha - 6
            E_geom = (n_alpha * self.E_alpha) + (links * self.E_link)
            if rem == 2: E_geom += self.E_link
            if rem == 3: 
                E_geom += 3.5 * self.E_link
                if Z == 2: E_geom -= self.a_C
            if N != Z and A >= 4: 
                 E_geom -= (self.E_alpha * math.sqrt(2/3)) * ((N-Z)**2) / A 
            return E_geom
        else:
            E_vol = self.a_V * A
            E_surf = self.a_S * (A**(2.0/3.0))
            E_coul = self.a_C * (Z*(Z-1)) / (A**(1.0/3.0))
            E_sym = self.a_Sym * ((N-Z)**2) / A
            if Z % 2 == 0 and N % 2 == 0: E_pair = self.delta / (A**(0.5))
            elif Z % 2 != 0 and N % 2 != 0: E_pair = -self.delta / (A**(0.5))
            else: E_pair = 0
            E_macro = E_vol - E_surf - E_coul - E_sym + E_pair
            return E_macro - self.geometric_shell_penalty(Z, N)

def parse_ame2020(text_content):
    dataset = []
    lines = text_content.splitlines() # Универсальный разделитель
    for line in lines:
        if len(line) < 67 or line.startswith('1N-Z') or 'MASS EXCESS' in line or 'A T O M I C' in line:
            continue
        try:
            Z = int(line[9:14])
            A = int(line[14:19])
            el = line[20:23].strip()
            iso_name = f"{A}{el}"
            
            be_str = line[54:67].replace('#', '').strip()
            if not be_str or be_str == '*': continue
            
            real_be_mev = (A * float(be_str)) / 1000.0
            if real_be_mev > -100: 
                dataset.append((iso_name, Z, A, real_be_mev))
        except Exception:
            continue
    return dataset

def parse_nubase(text_content):
    nubase_data = {}
    unit_multipliers = {
        's': 1, 'ms': 1e-3, 'us': 1e-6, 'ns': 1e-9, 'ps': 1e-12,
        'fs': 1e-15, 'as': 1e-18, 'zs': 1e-21, 'ys': 1e-24,
        'm': 60, 'h': 3600, 'd': 86400, 'y': 3.1536e7,
        'ky': 3.1536e10, 'My': 3.1536e13, 'Gy': 3.1536e16, 'Py': 3.1536e22
    }
    
    lines = text_content.splitlines()
    for line in lines:
        if len(line) < 70 or line.startswith('#') or 'NUBASE' in line:
            continue
        try:
            zzzi = line[4:8].strip()
            if not zzzi.endswith('0'): continue # Только Ground States (основные состояния)
            
            iso_name = line[11:16].strip().replace(' ', '')
            
            hl_val_str = line[60:69].strip().replace('#', '').replace('>', '').replace('<', '').replace('~', '')
            hl_unit = line[69:72].strip()
            
            if 'stbl' in hl_unit.lower() or 'infty' in hl_val_str.lower() or 'stable' in hl_val_str.lower():
                nubase_data[iso_name] = float('inf')
            elif hl_val_str and hl_unit in unit_multipliers:
                nubase_data[iso_name] = float(hl_val_str) * unit_multipliers[hl_unit]
        except Exception:
            continue
    return nubase_data

# ==========================================================================================
# ИНТЕРФЕЙС
# ==========================================================================================
st.title("Simureality: Chronos Engine ⏳")
st.markdown("**Валидация Времени Жизни.** Доказательство связи Топологического долга ГЦК ($\Delta K$) и распада (NUBASE2020).")

# Ищем файлы в любом регистре
def find_file(possible_names):
    for name in possible_names:
        if os.path.exists(name): return name
    return None

ame_path = find_file(["mass.txt", "mass.mas20", "MASS.TXT", "MASS.MAS20"])
nub_path = find_file(["NUBASE2020.txt", "nubase2020.txt", "Nubase2020.txt"])

dataset_ame = None
dataset_nubase = None
engine = GridPhysicsEngine()

col1, col2 = st.columns(2)

# БЛОК ЗАГРУЗКИ AME2020
with col1:
    if ame_path:
        with open(ame_path, "r", encoding="utf-8", errors="ignore") as f:
            dataset_ame = parse_ame2020(f.read())
        st.success(f"✅ Массы загружены из гитхаба ({ame_path}). Найдено изотопов: {len(dataset_ame)}")
    else:
        upl_ame = st.file_uploader("Загрузить mass.txt (AME2020)", type=["txt", "mas20"])
        if upl_ame:
            dataset_ame = parse_ame2020(upl_ame.getvalue().decode("utf-8", errors="ignore"))
            st.success(f"Найдено изотопов: {len(dataset_ame)}")

# БЛОК ЗАГРУЗКИ NUBASE
with col2:
    if nub_path:
        with open(nub_path, "r", encoding="utf-8", errors="ignore") as f:
            dataset_nubase = parse_nubase(f.read())
        st.success(f"✅ Таймеры загружены из гитхаба ({nub_path}). Найдено таймеров: {len(dataset_nubase)}")
    else:
        upl_nubase = st.file_uploader("Загрузить NUBASE2020.txt", type=["txt"])
        if upl_nubase:
            dataset_nubase = parse_nubase(upl_nubase.getvalue().decode("utf-8", errors="ignore"))
            st.success(f"Найдено таймеров: {len(dataset_nubase)}")

st.divider()

# БЛОК РАСЧЕТОВ
if dataset_ame and dataset_nubase:
    st.info("Выполняю аппаратное слияние матриц (JOIN) и расчет $\Sigma K$...")
    
    results = []
    for name, Z, A, real_be in dataset_ame:
        if name in dataset_nubase:
            hl_sec = dataset_nubase[name]
            sim_val = engine.calculate_energy(Z, A)
            
            # Топологический долг (Абсолютная дельта)
            delta_k = abs(sim_val - real_be)
            
            if hl_sec == float('inf'):
                log_hl = 30 # Условно-стабильный (бесконечность)
                status = "Stable"
            else:
                log_hl = math.log10(hl_sec) if hl_sec > 0 else -30
                status = "Unstable"
                
            results.append({
                "Isotope": name,
                "Z": Z,
                "A": A,
                "ΔK Debt (MeV)": round(delta_k, 3),
                "Log10(T_1/2)": round(log
