import pandas as pd
import numpy as np

def simureality_v17_multiverse_final():
    print(f"{'='*100}")
    print(f" SIMUREALITY V17: MULTIVERSE COMPATIBILITY TEST (FINAL)")
    print(f" LOGIC: Changing the Reference Frame (Core Material)")
    print(f"{'='*100}")

    # --- DATASET ---
    candidates = [
        {'El': 'Au', 'Vol': 10.2, 'Yield': 20,  'CA': 0,     'Oxide': False},
        {'El': 'Ag', 'Vol': 10.2, 'Yield': 15,  'CA': 0,     'Oxide': False},
        {'El': 'Pt', 'Vol': 9.09, 'Yield': 140, 'CA': 0,     'Oxide': False},
        {'El': 'Pd', 'Vol': 8.86, 'Yield': 50,  'CA': 0,     'Oxide': False},
        {'El': 'Fe', 'Vol': 7.09, 'Yield': 250, 'CA': 0,     'Oxide': False}, # Dense!
        {'El': 'Ta', 'Vol': 10.8, 'Yield': 180, 'CA': 0,     'Oxide': False},
        {'El': 'Mo', 'Vol': 9.38, 'Yield': 450, 'CA': 0,     'Oxide': False},
        {'El': 'Zn', 'Vol': 9.16, 'Yield': 100, 'CA': 1.856, 'Oxide': False},
        {'El': 'Zr', 'Vol': 14.0, 'Yield': 250, 'CA': 1.593, 'Oxide': False}, # Fluffy!
        {'El': 'Al', 'Vol': 10.0, 'Yield': 30,  'CA': 0,     'Oxide': False}, # Al without oxide for pure geo check
        {'El': 'W',  'Vol': 9.53, 'Yield': 750, 'CA': 0,     'Oxide': False}, 
    ]

    # --- THE CORES (Universes) ---
    cores = [
        {'Name': 'TUNGSTEN (W)', 'Vol': 9.53},  # The Standard
        {'Name': 'COPPER (Cu)',   'Vol': 7.11}, # The Dense World
        {'Name': 'MAGNESIUM (Mg)','Vol': 14.0}, # The Fluffy World
    ]

    IDEAL_HCP_CA = 1.633

    for core in cores:
        print(f"\n>>> UNIVERSE: {core['Name']} [Ref Vol: {core['Vol']}]")
        print(f"{'Rank':<4} {'El':<3} {'Vol':<5} {'Diff%':<6} | {'FINAL':<6} | {'Status'}")
        print("-" * 60)
        
        results = []
        
        for cand in candidates:
            # Skip self check logic
            if cand['El'] == core['Name'].split()[0]: continue 
            if core['Name'].startswith('TUNGSTEN') and cand['El'] == 'W': continue
            
            # 1. STATIC INTERFACE
            vol_ratio = cand['Vol'] / core['Vol']
            pen_dens = abs(1 - vol_ratio) * 40.0 
            
            # Wetting Bonus
            bonus_wet = min(500.0 / cand['Yield'], 30.0)
            
            static_score = max(0.0, min(90 - pen_dens + bonus_wet, 100))
            
            # 2. METABOLISM (Absolute Health)
            meta_factor = 1.0
            
            # Noise
            if cand['CA'] > 0:
                distort = cand['CA'] / IDEAL_HCP_CA
                if abs(distort - 1.0) > 0.05:
                    meta_factor -= abs(distort - 1.0) * 2.0
            
            # Decoherence 
            if cand['Vol'] > 12.0:
                meta_factor -= 0.3
                
            # Plasticity
            if cand['Yield'] < 50:
                meta_factor += 0.1
                
            meta_factor = max(0.0, meta_factor)
            
            # 3. FINAL
            final_score = static_score * meta_factor
            
            results.append({
                'El': cand['El'],
                'Vol': cand['Vol'],
                'Diff': abs(1 - vol_ratio)*100,
                'Score': final_score
            })
            
        # FIX: list.sort with reverse=True
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        rank = 1
        # Show Top 5
        for res in results[:5]:
            note = ""
            if core['Name'].startswith('COPPER') and res['El'] == 'Fe': note = "<-- IRON RISES"
            if core['Name'].startswith('MAGNESIUM') and res['El'] == 'Zr': note = "<-- ZIRCONIUM RISES"
            
            print(f"#{rank:<3} {res['El']:<3} {res['Vol']:<5} {res['Diff']:<6.1f} | {res['Score']:<6.1f} | {note}")
            rank += 1
            
        # Show Bottom
        print("...")
        for res in results[-2:]:
            print(f"BOT  {res['El']:<3} {res['Vol']:<5} {res['Diff']:<6.1f} | {res['Score']:<6.1f} | MISMATCH")

simureality_v17_multiverse_final()
