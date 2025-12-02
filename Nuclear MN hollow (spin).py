import numpy as np
import matplotlib.pyplot as plt
from itertools import product

# --- GEOMETRIC CONSTANTS ---
# Interaction threshold: nearest neighbors in FCC lattice (dist^2 = 2)
# We check dist^2 < 2.1 for float safety.
THRESHOLD_SQ = 2.1

def spin_phase_scan(max_n=45):
    # --- 1. LATTICE PREPARATION ---
    # Generate large FCC grid points (up to r_max=5)
    r_max = 5
    lattice_coords = []
    for x in range(-r_max, r_max+1):
        for y in range(-r_max, r_max+1):
            for z in range(-r_max, r_max+1):
                if (abs(x)+abs(y)+abs(z)) % 2 == 0: # Ensures points are on the FCC sublattice
                    lattice_coords.append(np.array([x, y, z]))
    
    lattice = np.array(lattice_coords)
    radii = np.linalg.norm(lattice, axis=1)
    radii[radii == 0] = 0.1 # Epsilon for center (avoid div by zero in potential)
    
    # --- 2. PHASE SCAN PARAMETERS ---
    # We test Alpha (Spin Intensity) from 0.0 (Static) to 3.0 (High Spin)
    alphas = np.linspace(0, 3.0, 31) 
    
    # Heatmap storage: rows=alpha, columns=N
    heatmap_gain = np.zeros((len(alphas), max_n + 1))
    
    # --- 3. DYNAMIC ACCRETION LOOP ---
    
    for i, alpha in enumerate(alphas):
        
        cluster = []
        occupied_indices = set()
        
        # Calculate Scores for all available lattice points
        # Score = Bonds (Attraction) - Radius Penalty (Gravity) - Alpha Penalty (Centrifugal)
        
        # Base Potential Terms (calculated once per alpha)
        # 1. Gravity (Confining potential, simple linear term)
        gravity_penalty = radii * 1.0 
        # 2. Centrifugal Potential (Force pushing outward: 1/r^2)
        centrifugal_penalty = alpha / (radii**2) 
        
        # We enforce a constant score template
        
        # Accrete from N=1 to Max_N
        for n in range(1, max_n + 1):
            
            # A. Calculate Bonds for all UNOCCUPIED points to the current cluster
            bonds_vec = np.zeros(len(lattice))
            
            if n == 1:
                # First particle: choose the spot with lowest total penalty (r=0)
                # But to start the simulation correctly, we just place it at the origin
                best_idx = np.argmin(radii)
                bonds_vec[best_idx] = 0
            else:
                # Calculate new bonds formed if any unoccupied point is chosen
                for current_atom in cluster:
                    d2 = np.sum((lattice - current_atom)**2, axis=1)
                    # Add 1 to bonds_vec for every near neighbor
                    bonds_vec += (d2 < THRESHOLD_SQ) * 1
                
            # B. Apply Full Scoring Hamiltonian (Maximize Stability Score)
            # Score = Attraction - Penalties
            # Note: We must ensure occupied points are masked or given a terrible score
            
            # Set occupied points to minimum score so they are never chosen again
            score_mask = np.full(len(lattice), -np.inf)
            
            for idx in range(len(lattice)):
                if tuple(lattice[idx]) not in occupied_indices:
                    # Score = Attraction - Gravity - Centrifugal Penalty
                    score_mask[idx] = (bonds_vec[idx] * 2.5) - gravity_penalty[idx] - centrifugal_penalty[idx]
            
            # Find the best unoccupied spot
            best_idx = np.argmax(score_mask)
            
            # C. Add Winner to Cluster
            best_atom = lattice[best_idx]
            cluster.append(best_atom)
            occupied_indices.add(tuple(best_atom))
            
            # D. Record Gain (Actual bonds formed by this particle)
            # This is simpler: the gain is simply the attraction term that generated the high score
            final_bonds_added = bonds_vec[best_idx]
            heatmap_gain[i, n] = final_bonds_added

    # --- 4. PLOTTING THE PHASE DIAGRAM ---
    
    # We display data from N=2 upwards, as N=1 is always 0 bonds
    plt.figure(figsize=(12, 10))
    
    # Use array N=2 to max_n
    n_plot = np.arange(2, max_n + 1)
    
    # Extract the relevant slice of the heatmap (excluding column 0 and 1 if we started from N=1)
    # The data is stored in columns 2 to 45 (for N=2 to N=45)
    data_to_plot = heatmap_gain[:, 2:max_n+1]
    
    # Plot Heatmap
    plt.imshow(data_to_plot, aspect='auto', cmap='magma', origin='lower',
               extent=[2, max_n, 0, 3.0])
    
    plt.colorbar(label='Stability Gain (Bonds formed)')
    
    plt.title('Simureality Phase Diagram: From Solid Core to Hollow Shell', fontsize=16)
    plt.xlabel('Nucleon Number (N)', fontsize=14)
    plt.ylabel('Spin Parameter (Alpha)', fontsize=14)
    
    # Annotate critical zones
    plt.axvline(x=20, color='lime', linestyle='--', alpha=0.8, label='N=20 (Calcium)')
    plt.axvline(x=28, color='cyan', linestyle=':', alpha=0.8, label='N=28 (Nickel)')
    
    plt.legend(loc='upper right')
    
    filename = 'simureality_spin_phase_source.png'
    plt.savefig(filename)
    print(f"Generated Phase Diagram: {filename}")
    return filename

if __name__ == '__main__':
    spin_file = spin_phase_scan()
    print(f"Code for Spin Phase Scanner provided in Python block above. Result saved to {spin_file}")
