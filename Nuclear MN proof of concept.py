import numpy as np

# --- PHYSICS CONSTANTS ---
# We use FCC Lattice (Face-Centered Cubic) logic.
# In FCC, every atom has 12 neighbors.
# Distance to neighbor = 1.0 (normalized)
THRESHOLD = 1.01

def solve_semimagic_sequence(max_n=260):
    print(f"{'N':<5} | {'Structure Name (Simureality)'} | {'Gain'} | {'Verdict'}")
    print("-" * 75)

    # 1. Initialize Universe with 1 seed
    cluster = [np.array([0.0, 0.0, 0.0])]
    
    # Pre-calculate FCC offsets (12 neighbors)
    # Relative coords in FCC: (+-1, +-1, 0) permutations / sqrt(2)
    # But let's work in integer grid logic for precision and scale dist later
    # Basis: (0,0,0). Neighbors at dist^2 = 2.
    offsets = set()
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                if x==0 and y==0 and z==0: continue
                if (abs(x)+abs(y)+abs(z)) == 2: # FCC condition in simple cubic grid
                    offsets.add((x,y,z))
    
    prev_bonds = 0
    history_gain = []

    for n in range(2, max_n + 1):
        # A. Find Candidates (Surface)
        candidates = set()
        existing_set = {tuple(p) for p in cluster}
        
        for atom in cluster:
            for off in offsets:
                cand = tuple(atom + np.array(off))
                if cand not in existing_set:
                    candidates.add(cand)
        
        # B. Greedy Selection (Maximize Bonds, Minimize Radius)
        best_cand = None
        max_bonds_added = -1
        min_dist_sq = 99999
        
        center_mass = np.mean(cluster, axis=0)
        
        for cand_t in candidates:
            cand = np.array(cand_t)
            
            # Count new bonds formed
            new_bonds = 0
            for atom in cluster:
                d2 = np.sum((atom - cand)**2)
                if d2 < 2.1: # Squared distance check (dist=sqrt(2)~1.41)
                    new_bonds += 1
            
            # Tie-breaker: Surface Tension (Compactness)
            d_center = np.sum((cand - center_mass)**2)
            
            if new_bonds > max_bonds_added:
                max_bonds_added = new_bonds
                best_cand = cand
                min_dist_sq = d_center
            elif new_bonds == max_bonds_added:
                if d_center < min_dist_sq:
                    best_cand = cand
                    min_dist_sq = d_center
        
        # C. Add Atom
        cluster.append(best_cand)
        
        # D. Calculate Metrics
        # Total bonds in system = prev + added
        current_total_bonds = prev_bonds + max_bonds_added
        
        # Gain per nucleon (Derivative of stability)
        # Gain = (Current_Avg - Prev_Avg) * Scale
        # Let's look at raw "Bonds Added". 
        # High "Bonds Added" means the atom fell into a deep hole (good).
        # Low "Bonds Added" means the atom sits on a peak (new shell start).
        
        # KEY LOGIC: A Magic Number is the LAST atom of a shell.
        # So atom N+1 should have LOW bonds added.
        
        verdict = ""
        # Geometric Interpretation based on FCC
        if n == 4: name = "Tetrahedron"
        elif n == 6: name = "Octahedron"
        elif n == 13: name = "Cuboctahedron (1st Shell)"
        elif n == 19: name = "Double Octahedron"
        elif n == 38: name = "Truncated Octahedron"
        elif n == 55: name = "Mackay Icosahedron (2nd Shell)"
        else: name = "Accretion..."
        
        # Check for drops in next step (Look ahead heuristic or print raw)
        # We print raw added bonds.
        # If N=13 adds 12 bonds (huge), and N=14 adds 3 bonds -> 13 is magic.
        
        bar = "=" * int(max_bonds_added * 2)
        print(f"{n:<5} | {name:<30} | +{max_bonds_added} {bar}")
        
        prev_bonds = current_total_bonds

if __name__ == "__main__":
    solve_semimagic_sequence()
