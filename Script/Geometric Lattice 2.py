import pandas as pd
import numpy as np

def simureality_v16_grand_tournament():
    print(f"{'='*100}")
    print(f" SIMUREALITY V16: THE GRAND MATERIALS LEADERBOARD")
    print(f" LOGIC: Dynamic Stress Test (Expanded Dataset N=18)")
    print(f"{'='*100}")

    # --- CONSTANTS (REFERENCE: TUNGSTEN) ---
    CORE_MAT = {'El': 'W', 'WF': 4.55, 'Vol': 9.53, 'Yield': 750}
    IDEAL_HCP_CA = 1.633
    
    # --- DATASET (EXPANDED) ---
    data = [
        # === THE NOBLE ONES (FCC) ===
        {'El': 'Au', 'Vol': 10.2, 'Yield': 20,  'CA': 0,     'Oxide': False}, # Gold
        {'El': 'Ag', 'Vol': 10.2, 'Yield': 15,  'CA': 0,     'Oxide': False}, # Silver
        {'El': 'Pt', 'Vol': 9.09, 'Yield': 140, 'CA': 0,     'Oxide': False}, # Platinum
        {'El': 'Pd', 'Vol': 8.86, 'Yield': 50,  'CA': 0,     'Oxide': False}, # Palladium
        {'El': 'Cu', 'Vol': 7.11, 'Yield': 70,  'CA': 0,     'Oxide': False}, # Copper
        
        # === THE HARD ONES (BCC/HCP) ===
        {'El': 'Mo', 'Vol': 9.38, 'Yield': 450, 'CA': 0,     'Oxide': False}, # Molybdenum
        {'El': 'Ta', 'Vol': 10.8, 'Yield': 180, 'CA': 0,     'Oxide': False}, # Tantalum
        {'El': 'Fe', 'Vol': 7.09, 'Yield': 250, 'CA': 0,     'Oxide': False}, # Iron
        {'El': 'Ti', 'Vol': 10.6, 'Yield': 350, 'CA': 1.587, 'Oxide': False}, # Titanium (Good HCP)
        
        # === THE ARMORED ONES ===
        {'El': 'Al', 'Vol': 10.0, 'Yield': 30,  'CA': 0,     'Oxide': True},  # Aluminum
        {'El': 'Ga', 'Vol': 11.8, 'Yield': 10,  'CA': 0,     'Oxide': True},  # Gallium
        {'El': 'Be', 'Vol': 4.85, 'Yield': 240, 'CA': 1.567, 'Oxide': True},  # Beryllium

        # === THE PROBLEM CHILDREN (Distorted/Fluffy) ===
        {'El': 'Zn', 'Vol': 9.16, 'Yield': 100, 'CA': 1.856, 'Oxide': False}, # Zinc
        {'El': 'Cd', 'Vol': 13.0, 'Yield': 30,  'CA': 1.886, 'Oxide': False}, # Cadmium
        {'El': 'Pb', 'Vol': 18.2, 'Yield': 10,  'CA': 0,     'Oxide': False}, # Lead
        {'El': 'Mg', 'Vol': 14.0, 'Yield': 90,  'CA': 1.624, 'Oxide': False}, # Magnesium
        {'El': 'Ca', 'Vol': 26.2, 'Yield': 12,  'CA': 0,     'Oxide': False}, # Calcium
        {'El': 'Zr', 'Vol': 14.0, 'Yield': 250, 'CA': 1.593, 'Oxide': False}, # Zirconium
    ]
    df = pd.DataFrame(data)

    # --- CALCULATION ENGINE (V15 Logic) ---

    # 1. INTERFACE SCORE (Static fit to Tungsten)
    vol_ratio = df['Vol'] / CORE_MAT['Vol']
    pen_dens = abs(1 - vol_ratio) * 40.0 
    bonus_wet = (500.0 / df['Yield']).clip(upper=30.0)
    
    # Base score logic
    df['Static_Score'] = (90 - pen_dens + bonus_wet).clip(0, 100)

    # 2. METABOLISM FACTOR (Dynamic health)
    def get_metabolism(row):
        factor = 1.0
        
        # A. NOISE (Distortion)
        if row['CA'] > 0:
            distort = row['CA'] / IDEAL_HCP_CA
            # Penalty for stretching (Zn, Cd) or compressing (Be) too much
            deviation = abs(distort - 1.0)
            if deviation > 0.05:
                factor -= deviation * 2.0 
        
        # B. DECOHERENCE (Density)
        if row['Vol'] > 12.0:
            factor -= 0.3 # Heavy penalty for fluffiness
            
        # C. PLASTICITY (Damping)
        if row['Yield'] < 50:
            factor += 0.1
            
        return max(0.0, factor)

    df['Meta_Factor'] = df.apply(get_metabolism, axis=1)
    df['Final_Score'] = df['Static_Score'] * df['Meta_Factor']

    # --- SORTING & REPORTING ---
    df = df.sort_values(by='Final_Score', ascending=False)

    print(f"{'Rank':<4} {'El':<3} {'Static':<8} {'Meta':<6} | {'FINAL':<6} | {'Class'}")
    print("-" * 60)
    
    rank = 1
    for i, row in df.iterrows():
        status = ""
        if row['Final_Score'] >= 100: status = "LEGENDARY"
        elif row['Final_Score'] >= 90: status = "ELITE"
        elif row['Final_Score'] >= 80: status = "EXCELLENT"
        elif row['Final_Score'] >= 60: status = "GOOD"
        elif row['Final_Score'] >= 40: status = "RISKY"
        else: status = "TRASH"
        
        star = "★" if status in ["LEGENDARY", "ELITE"] else ""
        
        print(f"#{rank:<3} {row['El']:<3} {row['Static_Score']:<8.1f} {row['Meta_Factor']:<6.2f} | {row['Final_Score']:<6.1f} | {status} {star}")
        rank += 1

simureality_v16_grand_tournament()
