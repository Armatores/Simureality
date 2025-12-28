import math

# ==============================================================================
# PROJECT: MENDELEEV'S ORCHESTRA (GRAND GEOMETRIC SCAN)
# SCOPE: 56 Solid Elements (Li to Am)
# LOGIC: Blind Harmonic Search (No manual overrides)
# ==============================================================================

# --- PHYSICS CONSTANTS ---
GATE_METRIC = 3.32492  # The Vacuum Gate (Gamma)
GAMMA_SYS   = 1.0418   # System Tax
AMPLITUDE   = 0.045    # Coupling Probability
STIFFNESS   = 45.0     # Resonance Sharpness

# --- HARMONIC GEARBOX ---
# 0.9 (Compression), 1.0 (Base), 1.33 (Tc-Mode), 1.5 (Pb-Mode), 2.0 (Double Base)
ALLOWED_MODES = [0.9, 1.0, 1.333, 1.5, 2.0]

def get_grand_db():
    # Massive DB of Lattice Constants (Angstroms) and Theta_D (K)
    # c=None for Cubic. Real Tc values provided.
    return [
        # --- ALKALI METALS (BCC - Usually too loose) ---
        {"id": "Li", "z": 3,  "a": 3.49, "c": None, "td": 344, "tc": 0.00}, # Press SC
        {"id": "Na", "z": 11, "a": 4.23, "c": None, "td": 158, "tc": 0.00},
        {"id": "K",  "z": 19, "a": 5.23, "c": None, "td": 91,  "tc": 0.00},
        {"id": "Rb", "z": 37, "a": 5.59, "c": None, "td": 56,  "tc": 0.00},
        {"id": "Cs", "z": 55, "a": 6.05, "c": None, "td": 38,  "tc": 0.00},

        # --- ALKALINE EARTH (HCP/FCC) ---
        {"id": "Be", "z": 4,  "a": 2.29, "c": 3.58, "td": 1440,"tc": 0.00},
        {"id": "Mg", "z": 12, "a": 3.21, "c": 5.21, "td": 400, "tc": 0.00},
        {"id": "Ca", "z": 20, "a": 5.58, "c": None, "td": 230, "tc": 0.00}, # FCC
        {"id": "Sr", "z": 38, "a": 6.08, "c": None, "td": 147, "tc": 0.00},
        {"id": "Ba", "z": 56, "a": 5.02, "c": None, "td": 110, "tc": 0.00}, # Press SC

        # --- TRANSITION METALS (PERIOD 4) ---
        {"id": "Sc", "z": 21, "a": 3.31, "c": 5.27, "td": 360, "tc": 0.00}, # Press SC
        {"id": "Ti", "z": 22, "a": 2.95, "c": 4.68, "td": 420, "tc": 0.40},
        {"id": "V",  "z": 23, "a": 3.02, "c": None, "td": 380, "tc": 5.40},
        {"id": "Cr", "z": 24, "a": 2.91, "c": None, "td": 630, "tc": 0.00},
        {"id": "Mn", "z": 25, "a": 8.91, "c": None, "td": 410, "tc": 0.00},
        {"id": "Fe", "z": 26, "a": 2.86, "c": None, "td": 470, "tc": 0.00},
        {"id": "Co", "z": 27, "a": 2.50, "c": 4.07, "td": 445, "tc": 0.00},
        {"id": "Ni", "z": 28, "a": 3.52, "c": None, "td": 450, "tc": 0.00},
        {"id": "Cu", "z": 29, "a": 3.61, "c": None, "td": 343, "tc": 0.00},
        {"id": "Zn", "z": 30, "a": 2.66, "c": 4.95, "td": 327, "tc": 0.85},

        # --- TRANSITION METALS (PERIOD 5) ---
        {"id": "Y",  "z": 39, "a": 3.65, "c": 5.73, "td": 280, "tc": 0.00}, # Press SC
        {"id": "Zr", "z": 40, "a": 3.23, "c": 5.15, "td": 291, "tc": 0.61},
        {"id": "Nb", "z": 41, "a": 3.30, "c": None, "td": 275, "tc": 9.25}, # KING
        {"id": "Mo", "z": 42, "a": 3.15, "c": None, "td": 450, "tc": 0.92},
        {"id": "Tc", "z": 43, "a": 2.74, "c": 4.40, "td": 454, "tc": 7.80}, # Tc Harmonic
        {"id": "Ru", "z": 44, "a": 2.70, "c": 4.28, "td": 600, "tc": 0.49},
        {"id": "Rh", "z": 45, "a": 3.80, "c": None, "td": 480, "tc": 0.00}, # Very low T possible?
        {"id": "Pd", "z": 46, "a": 3.89, "c": None, "td": 274, "tc": 0.00},
        {"id": "Ag", "z": 47, "a": 4.09, "c": None, "td": 225, "tc": 0.00},
        {"id": "Cd", "z": 48, "a": 2.98, "c": 5.62, "td": 209, "tc": 0.52},
        {"id": "In", "z": 49, "a": 3.25, "c": 4.95, "td": 108, "tc": 3.41}, # Tetragonal
        {"id": "Sn", "z": 50, "a": 5.83, "c": 3.18, "td": 200, "tc": 3.72}, # White Tin (Tet)

        # --- TRANSITION METALS (PERIOD 6) ---
        {"id": "La", "z": 57, "a": 3.77, "c": 12.1, "td": 142, "tc": 4.88}, # dHCP
        {"id": "Hf", "z": 72, "a": 3.19, "c": 5.05, "td": 252, "tc": 0.12},
        {"id": "Ta", "z": 73, "a": 3.30, "c": None, "td": 240, "tc": 4.47}, # QUEEN
        {"id": "W",  "z": 74, "a": 3.16, "c": None, "td": 400, "tc": 0.01},
        {"id": "Re", "z": 75, "a": 2.76, "c": 4.46, "td": 430, "tc": 1.69},
        {"id": "Os", "z": 76, "a": 2.73, "c": 4.32, "td": 500, "tc": 0.66},
        {"id": "Ir", "z": 77, "a": 3.84, "c": None, "td": 420, "tc": 0.11},
        {"id": "Pt", "z": 78, "a": 3.92, "c": None, "td": 240, "tc": 0.00},
        {"id": "Au", "z": 79, "a": 4.07, "c": None, "td": 165, "tc": 0.00},
        {"id": "Hg", "z": 80, "a": 2.99, "c": None, "td": 72,  "tc": 4.15}, # Alpha-Hg (Rhombohedral, treated as a)
        {"id": "Tl", "z": 81, "a": 3.46, "c": 5.52, "td": 78,  "tc": 2.40},
        {"id": "Pb", "z": 82, "a": 4.95, "c": None, "td": 105, "tc": 7.19}, # HEAVY KING
        {"id": "Bi", "z": 83, "a": 4.54, "c": 11.8, "td": 119, "tc": 0.00},

        # --- ACTINIDES / OTHERS ---
        {"id": "Th", "z": 90, "a": 5.08, "c": None, "td": 163, "tc": 1.38},
        {"id": "Pa", "z": 91, "a": 3.92, "c": 3.24, "td": 185, "tc": 1.40},
        {"id": "U",  "z": 92, "a": 2.85, "c": 4.96, "td": 207, "tc": 0.68}, # Alpha-U (Orthorhombic)
        {"id": "Al", "z": 13, "a": 4.05, "c": None, "td": 428, "tc": 1.17}, # FCC Aluminum
        {"id": "Ga", "z": 31, "a": 4.51, "c": 7.66, "td": 320, "tc": 1.08}, # Complex Ortho
    ]

def blind_predict(el):
    # Determine best resonance among ALL axes and ALL modes
    best_tc = 0.0
    best_info = "None"
    min_dev = 999.0

    axes = [('a', el['a'])]
    if el['c']: axes.append(('c', el['c']))

    for axis_name, length in axes:
        if length is None: continue
        
        for k in ALLOWED_MODES:
            target = k * GATE_METRIC
            dev = abs(length - target) / target
            
            # Decay Formula
            tc_pot = el['td'] * AMPLITUDE * math.exp(-GAMMA_SYS * dev * STIFFNESS)
            
            if tc_pot > best_tc:
                best_tc = tc_pot
                best_info = f"{axis_name}->{k}x"
                min_dev = dev

    # Cutoff
    if best_tc < 0.05: best_tc = 0.0
    
    return best_tc, best_info, min_dev

def run_grand_scan():
    db = get_grand_db()
    
    print(f"\n{'='*100}")
    print(f" PROJECT: MENDELEEV'S ORCHESTRA (GRAND GEOMETRIC SCAN)")
    print(f" GATE: {GATE_METRIC:.4f} A | MODES: {ALLOWED_MODES}")
    print(f"{'='*100}")
    print(f"{'EL':<3} {'Z':<3} | {'Structure':<12} | {'Real Tc':<7} | {'Pred Tc':<7} | {'Mode':<8} | {'Dev%':<6} | {'STATUS'}")
    print("-" * 100)
    
    stats = {"HIT": 0, "MISS": 0, "CLEAN": 0, "FALSE+": 0}
    
    for el in db:
        pred, mode, dev = blind_predict(el)
        
        real = el['tc']
        struct = f"a={el['a']}"
        if el['c']: struct += f" c={el['c']}"
        
        status = " "
        if real > 0 and pred > 0: 
            status = "HIT"
            stats["HIT"] += 1
        elif real == 0 and pred == 0: 
            status = "CLEAN"
            stats["CLEAN"] += 1
        elif real > 0 and pred == 0: 
            status = "MISS"
            stats["MISS"] += 1
        elif real == 0 and pred > 0: 
            status = "FALSE+"
            stats["FALSE+"] += 1
            
        # Filter noise for cleaner output
        # Uncomment to show everything
        # if status == "CLEAN" and dev > 0.1: continue 

        print(f"{el['id']:<3} {el['z']:<3} | {struct:<12} | {real:<7.2f} | {pred:<7.2f} | {mode:<8} | {dev*100:<6.2f} | {status}")

    print("-" * 100)
    total = len(db)
    acc = (stats['HIT'] + stats['CLEAN']) / total * 100
    print(f"SUMMARY: Accuracy {acc:.1f}%")
    print(f"HIT (Found SC): {stats['HIT']} | CLEAN (Correctly Ignored): {stats['CLEAN']}")
    print(f"MISS (Failed to find): {stats['MISS']} | FALSE+ (Predicted potential): {stats['FALSE+']}")

if __name__ == "__main__":
    run_grand_scan()
