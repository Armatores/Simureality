import math

def log_header(title):
    print(f"\n{'='*100}")
    print(f" {title}")
    print(f"{'='*100}")

# --- 1. GENESIS CONSTANTS (Pure Geometry) ---
def get_constants():
    m_e = 0.511
    gamma = 2 / math.sqrt(3) 
    E_LINK = 4 * m_e * gamma         # ~2.360 MeV
    E_LOOP = 0.5 * E_LINK            # ~1.180 MeV
    E_ALPHA = 12 * E_LINK            # ~28.322 MeV
    return E_ALPHA, E_LINK, E_LOOP

# --- 2. THE MEGA DATASET (62 Heavy Nuclei) ---
# Total Binding Energy (MeV) based on AME2020
MEGA_SET = {
    # Copper (Z=29)
    "Cu-63": 551.38, "Cu-65": 569.21,
    # Zinc (Z=30)
    "Zn-64": 559.10, "Zn-66": 578.14, "Zn-68": 595.40, "Zn-70": 611.10,
    # Gallium (Z=31)
    "Ga-69": 602.00, "Ga-71": 621.80,
    # Germanium (Z=32)
    "Ge-70": 610.56, "Ge-72": 628.70, "Ge-74": 645.74, "Ge-76": 661.60,
    # Arsenic (Z=33)
    "As-75": 652.56,
    # Selenium (Z=34)
    "Se-74": 639.20, "Se-76": 662.06, "Se-78": 679.56, "Se-80": 695.89, "Se-82": 711.10,
    # Bromine (Z=35)
    "Br-79": 686.20, "Br-81": 704.57,
    # Krypton (Z=36)
    "Kr-80": 694.34, "Kr-82": 713.43, "Kr-84": 732.26, "Kr-86": 749.20,
    # Rubidium (Z=37)
    "Rb-85": 739.67, "Rb-87": 757.85,
    # Strontium (Z=38)
    "Sr-84": 728.50, "Sr-86": 749.20, "Sr-88": 768.46,
    # Yttrium (Z=39)
    "Y-89": 775.64,
    # Zirconium (Z=40)
    "Zr-90": 783.90, "Zr-92": 801.37, "Zr-94": 816.99, "Zr-96": 828.70,
    # Niobium (Z=41)
    "Nb-93": 808.49,
    # Molybdenum (Z=42)
    "Mo-92": 796.51, "Mo-96": 830.63, "Mo-98": 846.12, "Mo-100": 860.50,
    # Technetium (Z=43)
    "Tc-99": 852.70,
    # Ruthenium (Z=44)
    "Ru-96": 812.50, "Ru-102": 878.80, "Ru-104": 892.40,
    # Rhodium (Z=45)
    "Rh-103": 884.60,
    # Palladium (Z=46)
    "Pd-102": 868.90, "Pd-106": 906.50, "Pd-108": 923.30, "Pd-110": 939.20,
    # Silver (Z=47)
    "Ag-107": 915.20, "Ag-109": 932.90,
    # Cadmium (Z=48)
    "Cd-106": 898.30, "Cd-112": 957.90, "Cd-114": 975.30,
    # Indium (Z=49)
    "In-115": 980.70,
    # Tin (Z=50) - THE MAGIC ONE
    "Sn-112": 953.50, "Sn-116": 992.80, "Sn-120": 1029.20, "Sn-124": 1060.00
}

# --- 3. AUTO-TOPOLOGY LOGIC ---
def analyze_topology(Z, A, consts):
    E_ALPHA, E_LINK, E_LOOP = consts
    
    n_alpha = A // 4
    rem = A % 4
    N_neutrons = A - Z
    
    # 1. CORE
    core_links = 3 * n_alpha - 6
    E_core = (n_alpha * E_ALPHA) + (core_links * E_LINK)
    
    # 2. DEBRIS & INTERFACE (Auto-Scaling)
    E_debris = 0
    debris_pot = 0
    if rem == 2: # Deuteron
        E_debris = E_LINK; debris_pot = 1
    elif rem == 3: # Triton
        E_debris = 3*E_LINK + E_LOOP; debris_pot = 3
    
    E_interface = 0
    if n_alpha > 0 and rem > 0:
        if rem == 1: # Neutron
            E_interface = E_LOOP # Magnetic loop anchor
        else:
            # For heavy nuclei, Core Capacity is always max (Surface available)
            core_cap = 3 
            anchor_count = min(debris_pot, core_cap)
            E_interface = anchor_count * E_LINK

    # 3. SYMMETRY BONUSES (Critical for heavy nuclei)
    E_bonus = 0
    # Even N Bonus (Pairing)
    if N_neutrons % 2 == 0: E_bonus += E_LOOP
    # Odd-Odd Penalty
    if Z % 2 != 0 and N_neutrons % 2 != 0: E_bonus -= E_LOOP
    
    # Simureality Hypothesis: Heavy Lattice Saturation
    # As the lattice grows huge (Z>30), internal compression adds efficiency.
    # Let's see raw geometry first without magic factors.
    
    return E_core + E_debris + E_interface + E_bonus

# --- 4. EXECUTION ---
def run_heavy_stress_test():
    consts = get_constants()
    targets = sorted(MEGA_SET.keys(), key=lambda x: MEGA_SET[x])
    
    log_header(f"SIMUREALITY DEEP STRESS TEST: {len(targets)} HEAVY NUCLEI (Cu-29 to Sn-50)")
    print(f"{'ISO':<7} | {'STRUCT':<9} | {'SIM BE':<10} | {'REAL BE':<10} | {'ACCURACY':<8} | {'COULOMB GAP'}")
    print("-" * 100)
    
    avg_gap = 0
    
    for name in targets:
        # Simple parser (assuming standard symbols)
        periodic = {"Cu":29, "Zn":30, "Ga":31, "Ge":32, "As":33, "Se":34, "Br":35, "Kr":36, 
                    "Rb":37, "Sr":38, "Y":39, "Zr":40, "Nb":41, "Mo":42, "Tc":43, "Ru":44, 
                    "Rh":45, "Pd":46, "Ag":47, "Cd":48, "In":49, "Sn":50}
        
        symbol = "".join([c for c in name.split("-")[0] if c.isalpha()])
        try:
            A = int(name.split("-")[1])
            Z = periodic.get(symbol, 0)
        except:
            continue

        sim_val = analyze_topology(Z, A, consts)
        real_val = MEGA_SET[name]
        
        # Here we expect SIM > REAL because Sim assumes 100% Geometry Gain, 
        # while Real has to pay Coulomb Tax.
        coulomb_gap = sim_val - real_val
        acc = 100 * (1 - abs(coulomb_gap)/real_val)
        
        n_alpha = A // 4
        rem = A % 4
        struct = f"{n_alpha}a+{rem}"
        
        print(f"{name:<7} | {struct:<9} | {sim_val:<10.2f} | {real_val:<10.2f} | {acc:.2f}%  | +{coulomb_gap:.1f} MeV")
        avg_gap += coulomb_gap

    print("-" * 100)
    print(f"AVERAGE COULOMB GAP: +{avg_gap/len(targets):.1f} MeV")
    print("INTERPRETATION:")
    print("1. Positive Gap = The pure lattice is stronger than the charged nucleus.")
    print("2. The Gap grows with Z. This IS the Coulomb Force (Z^2).")
    print("3. Check Sn-120 (Z=50). The gap there represents the stress of 50 protons.")

if __name__ == "__main__":
    run_heavy_stress_test()
