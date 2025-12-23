import pandas as pd
import numpy as np

def simureality_v18_cryogenics_fixed():
    print(f"{'='*100}")
    print(f" SIMUREALITY V18: CRYOGENIC PROTOCOL (300K vs 4K) - FIXED")
    print(f" LOGIC: As T -> 0, Entropy Tax vanishes. Superconductivity emerges.")
    print(f"{'='*100}")

    # --- CONSTANTS ---
    CORE_MAT = {'El': 'W', 'Vol': 9.53, 'Yield': 750} 
    IDEAL_HCP_CA = 1.633
    
    # --- DATASET ---
    data = [
        {'El': 'Au', 'Vol': 10.2, 'Yield': 20,  'CA': 0,     'Oxide': False, 'Tc': 0.0},
        {'El': 'Cu', 'Vol': 7.11, 'Yield': 70,  'CA': 0,     'Oxide': False, 'Tc': 0.0},
        {'El': 'Al', 'Vol': 10.0, 'Yield': 30,  'CA': 0,     'Oxide': True,  'Tc': 1.2},  
        {'El': 'Pb', 'Vol': 18.2, 'Yield': 10,  'CA': 0,     'Oxide': False, 'Tc': 7.2},  # SUPERCONDUCTOR!
        {'El': 'Nb', 'Vol': 10.8, 'Yield': 200, 'CA': 0,     'Oxide': False, 'Tc': 9.2},  # SUPERCONDUCTOR!
        {'El': 'Zn', 'Vol': 9.16, 'Yield': 100, 'CA': 1.856, 'Oxide': False, 'Tc': 0.85}, 
        {'El': 'Mg', 'Vol': 14.0, 'Yield': 90,  'CA': 1.624, 'Oxide': False, 'Tc': 0.0},
        {'El': 'Ca', 'Vol': 26.2, 'Yield': 12,  'CA': 0,     'Oxide': False, 'Tc': 0.0}, 
    ]
    
    # --- SIMULATION ENGINE ---
    
    def calculate_score(temp_kelvin, row):
        # 1. ENTROPY FACTOR
        thermal_noise = temp_kelvin / 300.0
        
        # 2. STATIC INTERFACE
        vol_ratio = row['Vol'] / CORE_MAT['Vol']
        pen_dens = abs(1 - vol_ratio) * 40.0
        
        # Wetting Bonus (FIXED: using min instead of clip)
        # При низких температурах пластичность падает, бонус уменьшаем
        wet_val = 500.0 / row['Yield']
        if temp_kelvin < 50:
             wet_val *= 0.5 # Замерзшее золото хуже смачивает
        bonus_wet = min(wet_val, 30.0)
        
        # Static Score Calc (FIXED: using max/min)
        raw_static = 90 - pen_dens + bonus_wet
        static_score = max(0.0, min(raw_static, 100.0))
        
        # 3. METABOLISM
        meta_factor = 1.0
        
        # A. SUPERCONDUCTIVITY CHECK (GOD MODE)
        if row['Tc'] > 0 and temp_kelvin < row['Tc']:
            return 999.0, "SUPER" 
            
        # B. NOISE PENALTY (Reduced by cold)
        if row['CA'] > 0:
            distort = row['CA'] / IDEAL_HCP_CA
            if abs(distort - 1.0) > 0.05:
                # Штраф уменьшается на холоде, но не исчезает
                base_penalty = abs(distort - 1.0) * 2.0
                correction = max(0.2, thermal_noise)
                meta_factor -= (base_penalty * correction)
        
        # C. DECOHERENCE (Density) - Рыхлость не лечится холодом
        if row['Vol'] > 12.0:
            meta_factor -= 0.3
            
        return static_score * meta_factor, "Normal"

    # --- RUN SCENARIOS ---
    print(f"{'El':<3} | {'300K (Warm)':<12} | {'4K (Cryo)':<12} | {'Effect'}")
    print("-" * 60)
    
    df = pd.DataFrame(data)
    
    for i, row in df.iterrows():
        score_warm, status_warm = calculate_score(300.0, row)
        score_cold, status_cold = calculate_score(4.0, row)
        
        # Format output
        w_str = f"{score_warm:.1f}"
        c_str = f"{score_cold:.1f}"
        if status_cold == "SUPER": c_str = "GOD MODE"
        
        effect = "Stable"
        if status_cold == "SUPER": 
            effect = "PHASE SHIFT!"
        elif score_cold > score_warm + 5:
            effect = "Improved"
        elif score_cold < score_warm - 5:
            effect = "Frozen" # Ухудшение из-за потери пластичности
            
        print(f"{row['El']:<3} | {w_str:<12} | {c_str:<12} | {effect}")

simureality_v18_cryogenics_fixed()
