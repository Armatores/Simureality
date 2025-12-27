import math

# ==============================================================================
# PROJECT: RESONANCE SEEKER (PURE 3D ELEMENTS EDITION)
# TARGET: Finding Geometric Resonance between Lattice 'a' at Tc and 
#         the Bohr Orbit Circumference (The "Rolling Electron" Model).
# ==============================================================================

def log_header(text):
    print(f"\n{'='*95}")
    print(f" {text}")
    print(f"{'='*95}")

# --- 1. PHYSICS CONSTANTS ---
ALPHA = 1 / 137.035999
# Bohr Radius (approx 0.529 Angstroms)
A0_BOHR = 0.529177 
# THE GATE METRIC: Circumference of the ground state orbit (2 * pi * r)
# Hypothesis: The electron "rolls" perfectly through the lattice hole of this size.
GATE_METRIC = 2 * math.pi * A0_BOHR  # ~3.3249 Angstroms

def get_pure_elements_db():
    # DATABASE OF PURE 3D SUPERCONDUCTING ELEMENTS
    # Data: Symbol, Name, Lattice Type, a_300K (Å), Tc (K), Therm_Exp (10^-6/K)
    # Excluded: Alloys, 2D materials, High-Pressure phases.
    db = [
        # GROUP 5 (The Champions)
        {"id": "Nb", "name": "Niobium",   "struct": "BCC", "a": 3.3004, "Tc": 9.25,  "alpha": 7.3},
        {"id": "V",  "name": "Vanadium",  "struct": "BCC", "a": 3.0240, "Tc": 5.40,  "alpha": 8.4},
        {"id": "Ta", "name": "Tantalum",  "struct": "BCC", "a": 3.3013, "Tc": 4.47,  "alpha": 6.3},
        
        # GROUP 4
        {"id": "Ti", "name": "Titanium",  "struct": "HCP", "a": 2.9508, "Tc": 0.40,  "alpha": 8.6}, # Using 'a' of HCP
        {"id": "Zr", "name": "Zirconium", "struct": "HCP", "a": 3.2320, "Tc": 0.61,  "alpha": 5.7},
        {"id": "Hf", "name": "Hafnium",   "struct": "HCP", "a": 3.1965, "Tc": 0.12,  "alpha": 5.9},

        # GROUP 6
        {"id": "Mo", "name": "Molybdenum","struct": "BCC", "a": 3.1470, "Tc": 0.915, "alpha": 4.8},
        {"id": "W",  "name": "Tungsten",  "struct": "BCC", "a": 3.1652, "Tc": 0.015, "alpha": 4.5},

        # GROUP 13 (Post-Transition)
        {"id": "Al", "name": "Aluminum",  "struct": "FCC", "a": 4.0495, "Tc": 1.175, "alpha": 23.1},
        {"id": "Ga", "name": "Gallium",   "struct": "Ortho","a": 4.5190, "Tc": 1.08,  "alpha": 18.0}, # Ga is complex
        {"id": "In", "name": "Indium",    "struct": "Tetra","a": 3.2512, "Tc": 3.41,  "alpha": 32.1}, # 'a' axis
        {"id": "Tl", "name": "Thallium",  "struct": "HCP", "a": 3.4566, "Tc": 2.38,  "alpha": 29.0},

        # GROUP 14
        {"id": "Sn", "name": "Tin (White)","struct": "Tetra","a": 5.8318, "Tc": 3.72,  "alpha": 22.0},
        {"id": "Pb", "name": "Lead",      "struct": "FCC", "a": 4.9508, "Tc": 7.19,  "alpha": 28.9},

        # GROUP 12
        {"id": "Zn", "name": "Zinc",      "struct": "HCP", "a": 2.6649, "Tc": 0.85,  "alpha": 30.2},
        {"id": "Cd", "name": "Cadmium",   "struct": "HCP", "a": 2.9790, "Tc": 0.51,  "alpha": 30.8},
        {"id": "Hg", "name": "Mercury",   "struct": "Rhomb","a": 2.9925, "Tc": 4.15,  "alpha": 60.4}, # The OG Superconductor

        # NOBLE METALS (Rare SC)
        {"id": "Ir", "name": "Iridium",   "struct": "FCC", "a": 3.8390, "Tc": 0.11,  "alpha": 6.4},
        
        # ACTINIDES (Exotic)
        {"id": "Th", "name": "Thorium",   "struct": "FCC", "a": 5.0842, "Tc": 1.38,  "alpha": 11.0},
        {"id": "U",  "name": "Uranium(a)","struct": "Ortho","a": 2.8540, "Tc": 0.68,  "alpha": 13.9}
    ]
    return db

def get_harmonic_match(ratio):
    # Musical/Geometric Ratios to check
    # 1:1 = Fundamental Resonance (The Tunnel)
    # 3:2 = Perfect Fifth (Mesh Locking)
    # 4:3 = Perfect Fourth
    # 5:4 = Major Third
    # 1:2 = Octave (Double frequency)
    # sqrt(2) = Diagonal fit
    
    harmonics = [
        (1.000, "1:1  [FUNDAMENTAL]"),
        (1.500, "3:2  [PERFECT FIFTH]"),
        (1.333, "4:3  [PERFECT FOURTH]"),
        (1.250, "5:4  [MAJOR THIRD]"),
        (1.200, "6:5  [MINOR THIRD]"),
        (0.866, "sqrt(3)/2 [HEIGHT]"), # Geometry factor
        (1.414, "sqrt(2) [DIAGONAL]"),
        (0.707, "1/sqrt(2) [HALF-DIAG]"),
        (0.900, "9:10 [GAP MODE]")
    ]
    
    best_h = None
    min_diff = 100
    
    for h_val, h_name in harmonics:
        diff = abs(ratio - h_val)
        if diff < min_diff:
            min_diff = diff
            best_h = (h_val, h_name)
            
    # Threshold for "Resonance"
    if min_diff < 0.025: # 2.5% tolerance
        return best_h[1], min_diff, best_h[0]
    return "---", min_diff, 0

def run_analysis():
    data = get_pure_elements_db()
    
    log_header(f"GRAND SCRIPT: 3D RESONANCE CHECK ({len(data)} ELEMENTS)")
    print(f"[*] TARGET GATE (Bohr Circumference): {GATE_METRIC:.5f} Å")
    print(f"[*] PHYSICS: Tc reached when Lattice(T) matches harmonic of Electron Wave.")
    print("-" * 95)
    print(f"{'EL':<3} | {'STRUCT':<5} | {'Tc(K)':<6} | {'a(Tc)':<7} | {'GATE(Å)':<7} | {'RATIO':<6} | {'RESONANCE TYPE'}")
    print("-" * 95)
    
    matches = 0
    
    for item in data:
        # 1. Thermal Contraction to Tc
        delta_T = item["Tc"] - 300.0
        # Linear expansion approximation: L = L0 * (1 + alpha * dT)
        a_Tc = item["a"] * (1 + (item["alpha"] * 1e-6 * delta_T))
        
        # 2. Calculate Ratio
        ratio = a_Tc / GATE_METRIC
        
        # 3. Check Harmonics
        match_name, diff, target = get_harmonic_match(ratio)
        
        # Formatting for "Hits"
        marker = ""
        if match_name != "---":
            matches += 1
            if "FUNDAMENTAL" in match_name:
                marker = "\033[92m[!!!]\033[0m" # Green (if terminal supports)
            elif "FIFTH" in match_name or "FOURTH" in match_name:
                 marker = "[!]"
        
        print(f"{item['id']:<3} | {item['struct']:<5} | {item['Tc']:<6.2f} | {a_Tc:<7.4f} | {GATE_METRIC:.4f}  | {ratio:<6.4f} | {marker} {match_name}")

    print("-" * 95)
    print(f"RESULTS: {matches} out of {len(data)} elements show Harmonic Locking.")
    print("\nOBSERVATIONS:")
    print("1. Look at the BCC metals (Nb, Ta, V). They are the cleanest.")
    print("2. Look at Aluminum (Al) and Lead (Pb) - do they hit integer ratios like 4:3 or 3:2?")
    print("3. If this holds, Superconductivity is simply 'Geometric Clearance'.")

if __name__ == "__main__":
    run_analysis()
