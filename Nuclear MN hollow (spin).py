import numpy as np
from itertools import product

# --- PHYSICS CONSTANTS ---
THRESHOLD_SQ = 2.1 # Bond distance check (dist^2 < 2.1)

def log_spin_phase_scan(max_n=45):
    # --- 1. SEEDING THE UNIVERSE ---
    np.random.seed(42) # Ensure identical results
    
    # --- 2. LATTICE PREPARATION ---
    r_max = 5
    lattice_coords = []
    for x in range(-r_max, r_max+1):
        for y in range(-r_max, r_max+1):
            for z in range(-r_max, r_max+1):
                if (abs(x)+abs(y)+abs(z)) % 2 == 0:
                    lattice_coords.append(np.array([x, y, z]))
    
    lattice = np.array(lattice_coords)
    radii = np.linalg.norm(lattice, axis=1)
    radii[radii == 0] = 0.1 # Epsilon for center (avoid div by zero in potential)
    
    # --- 3. PHASE SCAN PARAMETERS ---
    alphas = np.linspace(0, 3.0, 31) 
    
    # Heatmap storage: We store ALL data, but only print N=20 and N=28
    heatmap_gain = np.zeros((len(alphas), max_n + 1))
    
    # --- 4. DYNAMIC ACCRETION LOOP ---
    for i, alpha in enumerate(alphas):
        
        cluster = []
        occupied_indices = set()
        
        # Base Potential Terms
        gravity_penalty = radii * 1.0 
        centrifugal_penalty = alpha / (radii**2) 
        
        for n in range(1, max_n + 1):
            
            bonds_vec = np.zeros(len(lattice))
            
            # --- Score Calculation (Optimized) ---
            if n > 1:
                arr_cluster = np.array(cluster)
                for current_atom in arr_cluster:
                    d2 = np.sum((lattice - current_atom)**2, axis=1)
                    bonds_vec += (d2 < THRESHOLD_SQ) * 1
            
            # Full Scoring Hamiltonian (Maximize Stability Score)
            score_mask = np.full(len(lattice), -np.inf)
            
            for idx in range(len(lattice)):
                if tuple(lattice[idx]) not in occupied_indices:
                    # Score = Attraction - Gravity - Centrifugal Penalty
                    score_mask[idx] = (bonds_vec[idx] * 2.5) - gravity_penalty[idx] - centrifugal_penalty[idx]
            
            # Find the best unoccupied spot
            best_idx = np.argmax(score_mask)
            
            # Add Winner
            best_atom = lattice[best_idx]
            cluster.append(best_atom)
            occupied_indices.add(tuple(best_atom))
            
            # Record Gain (Actual bonds formed by this particle)
            final_bonds_added = bonds_vec[best_idx]
            heatmap_gain[i, n] = final_bonds_added

    # --- 5. TEXT OUTPUT ---
    
    print("\n--- SIMUREALITY SPIN PHASE LOG ---")
    print(f"| Alpha | N=20 (Calcium) | N=28 (Nickel) | N=32 (Fullerene) |")
    print("|-------|----------------|---------------|------------------|")
    
    for i, alpha in enumerate(alphas):
        # N=20 is index 20, N=28 is index 28, N=32 is index 32 (based on 1-indexing)
        # Note: Index 0 is N=0 (unused), Index 1 is N=1 (seed), Index 20 is N=20.
        gain_20 = heatmap_gain[i, 20]
        gain_28 = heatmap_gain[i, 28]
        gain_32 = heatmap_gain[i, 32]
        
        # Color coding heuristic (High gain = 5 or 6)
        c20 = '🟢' if gain_20 >= 5.0 else ''
        c28 = '🟢' if gain_28 >= 5.0 else ''
        c32 = '🟢' if gain_32 >= 5.0 else ''

        print(f"| {alpha:.2f} | {gain_20:.1f} {c20} | {gain_28:.1f} {c28} | {gain_32:.1f} {c32} |")
        
    print("--- End of Log ---")

if __name__ == '__main__':
    log_spin_phase_scan()

