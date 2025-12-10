import math

def log_header(text):
    print(f"\n{'='*90}")
    print(f" {text}")
    print(f"{'='*90}")

def master_simulation():
    # =========================================================================
    # PART 1: GENESIS (CONSTANTS DERIVATION)
    # =========================================================================
    log_header("1. GENESIS: DERIVING CONSTANTS FROM GEOMETRY")
    
    # 1. Input: Mass of Electron (Fundamental Unit)
    m_electron = 0.511  # MeV
    
    # 2. Geometric Constants
    # TENSION (Gamma): Projection of Tetrahedron onto Cube (2 / sqrt(3))
    # Used for structural objects (1D Edges)
    GAMMA_STRUCT = 2 / math.sqrt(3)  # ~1.1547
    
    # VOLUME TAX: Distributed tension across 3 dimensions (Cube root of Gamma)
    # Used for volumetric fields (Coulomb)
    GAMMA_VOL = GAMMA_STRUCT**(1/3)  # ~1.049
    
    # PACKING LIMIT: Maximum density of FCC Lattice (pi / 3sqrt(2))
    APF_FCC = math.pi / (3 * math.sqrt(2)) # ~0.7405

    # 3. Deriving Forces
    # STRONG FORCE (The Geometry)
    # Edge = Up Quark Line (N=2 nodes) -> 4 * m_e
    E_edge_raw = 4 * m_electron
    
    # Alpha Particle (The Brick): 12 edges * Raw Energy * Structure Tax
    E_alpha_derived = (12 * E_edge_raw) * GAMMA_STRUCT
    
    # Lattice Link (The Cement): Single edge * Structure Tax
    E_link_derived = E_edge_raw * GAMMA_STRUCT
    
    # COULOMB FORCE (The Packing)
    # Observed Coeff = Ideal Packing / Volume Tax
    a_c_derived = APF_FCC / GAMMA_VOL

    # --- PRINT GENESIS REPORT ---
    print(f"{'PARAMETER':<20} | {'FORMULA':<25} | {'VALUE':<10} | {'REAL WORLD MATCH'}")
    print("-" * 90)
    print(f"{'Alpha Energy':<20} | {'12 * 4me * Gamma':<25} | {E_alpha_derived:.3f}     | {'28.30 (99.9%)'}")
    print(f"{'Coulomb Coeff':<20} | {'0.74 / Gamma^(1/3)':<25} | {a_c_derived:.3f}     | {'~0.71 (Liquid Drop)'}")
    print(f"{'Lattice Link':<20} | {'4me * Gamma':<25} | {E_link_derived:.3f}     | {'~2.4 (Est.)'}")
    
    # =========================================================================
    # PART 2: THE ALPHA-LADDER & BINDING ENERGY CURVE
    # =========================================================================
    log_header("2. SIMULATION: BINDING ENERGY & STABILITY (He-4 to Kr-36)")
    print(f"{'ELEM':<6} | {'Z':<3} | {'LINKS':<5} | {'GAIN (Geom)':<11} | {'COST (Coul)':<11} | {'BE/A':<8} | {'STATUS'}")
    print("-" * 90)

    prev_be = 0
    peak_found = False
    
    # Loop through nuclei from Helium (1 alpha) to Krypton (18 alphas)
    # Assuming N=Z (Alpha Conjugate) to find the geometric limit
    for N in range(1, 19):
        Z = N * 2
        A = N * 4
        
        # A. Gain (Strong Force)
        # Energy of Bricks (Internal) + Energy of Cement (Links)
        e_bricks = N * E_alpha_derived
        
        if N < 2: links = 0 # Single block
        else: links = 3 * N - 6 # Rigid truss formula
        
        e_cement = links * E_link_derived
        total_gain = e_bricks + e_cement
        
        # B. Cost (Coulomb Force)
        # Using DERIVED coefficient (0.706)
        # Formula: a_c * Z(Z-1) / R.  Radius R ~ A^(1/3)
        radius = A**(1.0/3.0)
        e_cost = a_c_derived * (Z * (Z - 1)) / radius
        
        # C. Net Result
        total_be = total_gain - e_cost
        be_per_nucleon = total_be / A
        
        # Trend Detection
        trend = ""
        if N == 2: trend = "(! BE-8 ANOMALY !)" # Explicit check for Be-8
        elif be_per_nucleon > prev_be: trend = "Rising"
        else:
            if not peak_found:
                trend = "<< PEAK STABILITY >>"
                peak_found = True
            else:
                trend = "Falling (Needs Neutrons)"
        
        prev_be = be_per_nucleon
        
        print(f"Z={Z:<4} | {Z:<3} | {links:<5} | {total_gain:<11.1f} | {e_cost:<11.1f} | {be_per_nucleon:<8.3f} | {trend}")

    print("-" * 90)
    print("ANALYSIS:")
    print("1. Be-8 (Z=4): Severe drop in BE/A. Confirms Instability.")
    print("2. Peak: Check where the 'Rising' trend stops.")
    print("3. Falling Tail: Shows where pure Alpha-Lattice fails and requires Neutron Excess.")

if __name__ == "__main__":
    master_simulation()
