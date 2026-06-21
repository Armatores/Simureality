import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# Grid Physics Constants
# ---------------------------------------------------------
M_E = 0.51099895         
VOID = 939.565           
Z0 = 376.73              

PAYLOADS = {
    'u': (2**2) * M_E,   
    'd': (3**2) * M_E,   
    's': (14**2) * M_E,  
    'c': (50**2) * M_E,  
}

# ---------------------------------------------------------
# PDG Mapping Dictionary (Translating CERN names to Grid Rules)
# ---------------------------------------------------------
EXOTIC_MAP = {
    "D(s0)*(2317)": ("D_s0*(2317)", ['c', 's'], "1V"),           
    "chi(c1)(3872)": ("X(3872)", ['c', 'c', 'u', 'u'], "1V+Z0"), 
    "Z(c)(3900)": ("Z_c(3900)", ['c', 'c', 'u', 'd'], "1V+Z0"),  
    "T(cc)": ("T_cc+(3875)", ['c', 'c', 'u', 'd'], "1V+Z0"),     
    "P(c)(4312)": ("P_c(4312)", ['c', 'c', 'u', 'u', 'd'], "2V"),
    "P(c)(4440)": ("P_c(4440)", ['c', 'c', 'u', 'u', 'd'], "2V"),
    "Z(c)(4430)": ("Z_c(4430)", ['c', 'c', 'd', 'u'], "2V"),     
    "X(6900)": ("X(6900)", ['c', 'c', 'c', 'c'], "2V")           
}

@st.cache_data
def fetch_and_parse_pdg_data(filename="mass_width_2026.txt"):
    """
    Reads the local PDG FORTRAN file from the same directory as the script.
    """
    parsed_data = []

    # Проверяем, существует ли файл локально
    if not os.path.exists(filename):
        st.error(f"Файл {filename} не найден в корневой директории!")
        return pd.DataFrame()

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            if line.startswith('*') or len(line.strip()) == 0:
                continue
            
            try:
                if len(line) > 107:
                    raw_name = line[107:128].strip().split(' ')[0] 
                else:
                    continue

                if raw_name in EXOTIC_MAP:
                    readable_name, quarks, rule = EXOTIC_MAP[raw_name]
                    
                    mass_gev_str = line[33:51].strip()
                    mass_gev = float(mass_gev_str)
                    exp_mass_mev = mass_gev * 1000.0 

                    # --- Применяем Grid Physics ---
                    payload = sum(PAYLOADS[q] for q in quarks)
                    
                    if rule == "1V":
                        grid_mass = payload + VOID
                    elif rule == "1V+Z0":
                        grid_mass = payload + VOID + Z0
                    elif rule == "2V":
                        grid_mass = payload + (2 * VOID)
                    else:
                        grid_mass = 0

                    delta = abs(grid_mass - exp_mass_mev)

                    parsed_data.append({
                        "Particle": readable_name,
                        "Quarks": "".join(quarks),
                        "Grid Rule": rule,
                        "PDG Mass (MeV)": round(exp_mass_mev, 1),
                        "Grid Mass (MeV)": round(grid_mass, 1),
                        "Delta (MeV)": round(delta, 1)
                    })
            except Exception:
                continue

    except Exception as e:
        st.error(f"Ошибка при чтении файла: {e}")
        return pd.DataFrame()

    return pd.DataFrame(parsed_data)

# --- Пример вызова ---
# df_exotic = fetch_and_parse_pdg_data()
# st.dataframe(df_exotic)
