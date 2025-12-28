import math

# ==============================================================================
# SIMUREALITY ALLOY PREDICTOR V3.0 (PHYSICS-AWARE)
# Features:
# 1. Thermal Contraction: Projects 300K lattice to 0K.
# 2. VEC Filter (Matthias Rule): Penalizes VEC=6, Boosts VEC=5 & 7.
# 3. Geometric Resonance: Matches Vacuum Gate 3.325 A.
# ==============================================================================

# --- CONSTANTS ---
GATE_METRIC = 3.32492  # The Vacuum Truth
THERMAL_SHRINK = 0.998 # Approx 0.2% shrinkage from 300K to 0K
SYSTEM_TAX = 1.0418

# --- DB: Added 'vec' (Valence Electron Count) ---
def get_metal_db():
    return [
        {"id": "Ti", "a": 2.95, "vec": 4, "td": 420}, # Group 4
        {"id": "Zr", "a": 3.23, "vec": 4, "td": 291}, # Group 4 (HCP base)
        # Note: Zr in BCC solid solution is effective ~3.55-3.62. We use 3.60 for BCC mix logic.
        {"id": "Zr_bcc", "a": 3.60, "vec": 4, "td": 291, "hidden": True}, 
        
        {"id": "V",  "a": 3.02, "vec": 5, "td": 380}, # Group 5 (Peak)
        {"id": "Nb", "a": 3.30, "vec": 5, "td": 275}, # Group 5 (Peak)
        {"id": "Ta", "a": 3.306,"vec": 5, "td": 240}, # Group 5 (Peak)
        
        {"id": "Cr", "a": 2.91, "vec": 6, "td": 630}, # Group 6 (Valley)
        {"id": "Mo", "a": 3.15, "vec": 6, "td": 450}, # Group 6 (Valley)
        {"id": "W",  "a": 3.16, "vec": 6, "td": 400}, # Group 6 (Valley)
        
        {"id": "Mn", "a": 8.91, "vec": 7, "td": 410}, # Group 7
        {"id": "Tc", "a": 2.74, "vec": 7, "td": 454}, # Group 7 (Peak)
        {"id": "Re", "a": 2.76, "vec": 7, "td": 430}, # Group 7 (Peak)
        
        {"id": "Ru", "a": 2.70, "vec": 8, "td": 600}, 
        {"id": "Os", "a": 2.73, "vec": 8, "td": 500},
        
        {"id": "Rh", "a": 3.80, "vec": 9, "td": 480},
        {"id": "Ir", "a": 3.84, "vec": 9, "td": 420},
        
        {"id": "Pd", "a": 3.89, "vec": 10, "td": 274},
        {"id": "Pt", "a": 3.92, "vec": 10, "td": 240},
        
        {"id": "Cu", "a": 3.61, "vec": 11, "td": 343}, # Noble
        {"id": "Ag", "a": 4.09, "vec": 11, "td": 225},
        {"id": "Au", "a": 4.07, "vec": 11, "td": 165},
        
        {"id": "Al", "a": 4.05, "vec": 3,  "td": 428}, # p-element
        {"id": "Sn", "a": 5.83, "vec": 4,  "td": 200}, # p-element
        {"id": "Pb", "a": 4.95, "vec": 4,  "td": 105}, # p-element
    ]

# --- MATTHIAS RULE (VEC SCORING) ---
def get_vec_score(vec):
    # Ideal zones: 4.5-5.2 and 6.5-7.5
    # Dead zones: 4.0, 6.0, >9.0
    if 4.5 <= vec <= 5.3: return 1.0  # Nb, Ta zone
    if 6.4 <= vec <= 7.5: return 0.9  # Tc, Re zone
    if 5.7 <= vec <= 6.3: return 0.4  # Mo valley (Severe Penalty)
    if vec > 9.0: return 0.1          # Noble metals (Kill switch)
    if vec < 3.5: return 0.2          # Too empty
    return 0.6 # Neutral

# --- RESONANCE ENGINE ---
def calculate_alloy_potential(el1, el2, x):
    # 1. Hardware Mixing (Vegard's Law)
    a_mix_300k = el1['a'] * (1-x) + el2['a'] * x
    
    # 2. THERMAL CORRECTION (The "Cold Reality")
    a_mix_0k = a_mix_300k * THERMAL_SHRINK 
    
    # 3. Geometric Match (Vacuum Gate)
    # We look for 0.9x (2.99) or 1.0x (3.325)
    target_modes = [0.9, 1.0] 
    geo_score = 0
    best_mode = 0
    
    for k in target_modes:
        target = k * GATE_METRIC
        dev = abs(a_mix_0k - target) / target
        # Exponential sharpness (Resonance)
        score = math.exp(-150 * dev) 
        if score > geo_score:
            geo_score = score
            best_mode = k
            
    # 4. Software Mixing (VEC - Matthias Rule)
    vec_mix = el1['vec'] * (1-x) + el2['vec'] * x
    vec_factor = get_vec_score(vec_mix)
    
    # 5. Magnetic Veto
    magnetics = ['Cr', 'Mn', 'Fe', 'Co', 'Ni']
    if el1['id'] in magnetics or el2['id'] in magnetics:
        vec_factor *= 0.0 # Kill magnetics
        
    # TOTAL SCORE
    total_score = geo_score * vec_factor * 100
    
    return {
        "name": f"{el1['id']}({int((1-x)*100)}){el2['id']}({int(x*100)})",
        "score": total_score,
        "a_0k": a_mix_0k,
        "vec": vec_mix,
        "mode": best_mode
    }

def run_smart_scan():
    db = get_metal_db()
    results = []
    
    print(f"\n{'='*80}")
    print(f" SIMUREALITY V3.0: PHYSICS-AWARE SCANNER")
    print(f" Logic: Geometry (at 0K) + VEC (Matthias Rule)")
    print(f"{'='*80}")
    
    for i in range(len(db)):
        for j in range(i + 1, len(db)):
            el1 = db[i]
            el2 = db[j]
            if el1.get('hidden') or el2.get('hidden'): continue
            
            # Use special Zr_bcc for mixtures with Nb/Ta
            eff_el1 = el1
            eff_el2 = el2
            if el1['id'] == 'Zr' and el2['id'] in ['Nb', 'Ta', 'V']: eff_el1 = db[2] # Zr_bcc
            if el2['id'] == 'Zr' and el1['id'] in ['Nb', 'Ta', 'V']: eff_el2 = db[2] # Zr_bcc

            for x in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
                res = calculate_alloy_potential(eff_el1, eff_el2, x)
                if res['score'] > 10.0: # Only good candidates
                    results.append(res)

    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"{'ALLOY':<15} | {'a_0k':<7} | {'VEC':<5} | {'Mode':<5} | {'SCORE':<5}")
    print("-" * 80)
    
    seen = set()
    count = 0
    for res in results:
        base = "".join(sorted([c for c in res['name'] if c.isalpha()]))
        if base in seen and count > 15: continue
        seen.add(base)
        
        print(f"{res['name']:<15} | {res['a_0k']:<7.4f} | {res['vec']:<5.2f} | {res['mode']:<5.1f} | {res['score']:<5.1f}")
        count += 1
        if count > 20: break
    print("-" * 80)

if __name__ == "__main__":
    run_smart_scan()
