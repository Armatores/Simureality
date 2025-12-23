import pandas as pd
import numpy as np

def simureality_v18_cryogenics():
    print(f"{'='*100}")
    print(f" SIMUREALITY V18: CRYOGENIC PROTOCOL (300K vs 4K)")
    print(f" LOGIC: As T -> 0, Entropy Tax vanishes. Superconductivity emerges.")
    print(f"{'='*100}")

    # --- CONSTANTS ---
    CORE_MAT = {'El': 'W', 'Vol': 9.53, 'Yield': 750} # Tungsten Core
    IDEAL_HCP_CA = 1.633
    
    # --- DATASET (With Critical Temps Tc) ---
    # Tc = 0 means not a superconductor (at standard pressure)
    data = [
        {'El': 'Au', 'Vol': 10.2, 'Yield': 20,  'CA': 0,     'Oxide': False, 'Tc': 0.0},
        {'El': 'Cu', 'Vol': 7.11, 'Yield': 70,  'CA': 0,     'Oxide': False, 'Tc': 0.0},
        {'El': 'Al', 'Vol': 10.0, 'Yield': 30,  'CA': 0,     'Oxide': True,  'Tc': 1.2},  # Superconductor < 1.2K
        {'El': 'Pb', 'Vol': 18.2, 'Yield': 10,  'CA': 0,     'Oxide': False, 'Tc': 7.2},  # SUPERCONDUCTOR!
        {'El': 'Nb', 'Vol': 10.8, 'Yield': 200, 'CA': 0,     'Oxide': False, 'Tc': 9.2},  # SUPERCONDUCTOR!
        {'El': 'Zn', 'Vol': 9.16, 'Yield': 100, 'CA': 1.856, 'Oxide': False, 'Tc': 0.85}, # Weak SC
        {'El': 'Mg', 'Vol': 14.0, 'Yield': 90,  'CA': 1.624, 'Oxide': False, 'Tc': 0.0},
        {'El': 'Ca', 'Vol': 26.2, 'Yield': 12,  'CA': 0,     'Oxide': False, 'Tc': 0.0}, # Still fluffy
    ]
    
    # --- SIMULATION ENGINE ---
    
    def calculate_score(temp_kelvin, row):
        # 1. ENTROPY FACTOR (Temperature dependent)
        # При 300К фактор шума = 1.0. При 0К фактор = 0.0.
        thermal_noise = temp_kelvin / 300.0
        
        # 2. STATIC INTERFACE (Geometry doesn't change much)
        vol_ratio = row['Vol'] / CORE_MAT['Vol']
        pen_dens = abs(1 - vol_ratio) * 40.0
        
        # Wetting Bonus (Only works if there is thermal energy to move atoms)
        # При заморозке атомы "дубеют", пластичность падает.
        # Bonus scales with T slightly? Let's say it persists but less effective.
        bonus_wet = (500.0 / row['Yield']).clip(upper=30.0)
        
        static_score = (90 - pen_dens + bonus_wet).clip(0, 100)
        
        # 3. METABOLISM (The Dynamic Part)
        meta_factor = 1.0
        
        # A. SUPERCONDUCTIVITY CHECK (The Phase Transition)
        if row['Tc'] > 0 and temp_kelvin < row['Tc']:
            # PHASE TRANSITION!
            # Resistance -> 0. Entropy -> 0. Coherence -> Infinite.
            # Материал переходит в квантовое состояние.
            return 999.0, "SUPER" # GOD MODE
            
        # B. NOISE PENALTY (Scales with T)
        # Кривизна решетки (Zn) создает меньше проблем в холоде, но не исчезает.
        if row['CA'] > 0:
            distort = row['CA'] / IDEAL_HCP_CA
            if abs(distort - 1.0) > 0.05:
                # Penalty is reduced by cold (atoms don't rattle against defects)
                penalty = (abs(distort - 1.0) * 2.0) * max(0.2, thermal_noise) 
                meta_factor -= penalty
        
        # C. DECOHERENCE (Density)
        # Рыхлость никуда не девается. Вакуум есть вакуум.
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
        
        effect = "Stable"
        if status_cold == "SUPER": 
            c_str = "GOD MODE"
            effect = "PHASE SHIFT!"
        elif score_cold > score_warm + 5:
            effect = "Improved"
        elif score_cold < score_warm - 5:
            effect = "Frozen"
            
        print(f"{row['El']:<3} | {w_str:<12} | {c_str:<12} | {effect}")

simureality_v18_cryogenics()
