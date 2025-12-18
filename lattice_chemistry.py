import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import os

"""
Project Simureality: Lattice Chemistry Simulator
------------------------------------------------
This script demonstrates the emergence of chemical properties (Magic Numbers/Noble Gases)
from purely geometric constraints on a discrete lattice.

Hypothesis:
Atoms are not probability clouds, but geometric configurations of vectors (electrons)
minimizing tension on a vacuum grid (FCC Lattice).

Metric:
We minimize Total Energy = (Electron-Electron Repulsion) - (Nucleus-Electron Attraction).
"""

class LatticeChemistrySimulator:
    def __init__(self, r_max: int = 4):
        """
        Initialize the simulator with a grid size.
        :param r_max: Radius of the simulation box (in lattice units).
        """
        self.r_max = r_max
        self.lattice = self._generate_fcc_lattice()
        print(f"[Init] Generated FCC Lattice with {len(self.lattice)} nodes.")

    def _generate_fcc_lattice(self) -> np.ndarray:
        """Generates Face-Centered Cubic (FCC) lattice coordinates."""
        coords = []
        for x in range(-self.r_max, self.r_max + 1):
            for y in range(-self.r_max, self.r_max + 1):
                for z in range(-self.r_max, self.r_max + 1):
                    # FCC condition: x, y, z must have the same parity (sum is even)
                    if (x + y + z) % 2 == 0:
                        coords.append([x, y, z])
        
        lattice = np.array(coords, dtype=float)
        
        # Calculate distances from center (Nucleus)
        radii = np.linalg.norm(lattice, axis=1)
        
        # Remove the center point (occupied by Nucleus) and sort by proximity
        mask = radii > 0.1
        lattice = lattice[mask]
        radii = radii[mask]
        
        sorted_indices = np.argsort(radii)
        return lattice[sorted_indices]

    def _calculate_energy(self, config: np.ndarray, z_charge: int) -> float:
        """
        Calculates total electrostatic energy of a configuration.
        E = Repulsion (1/r_ij) - Attraction (Z/r_i)
        """
        n_electrons = len(config)
        if n_electrons == 0:
            return 0.0

        # 1. Attraction (Nucleus -> Electrons)
        # Force is proportional to Z (nucleus charge)
        r_i = np.linalg.norm(config, axis=1)
        attraction = np.sum(z_charge / r_i)

        # 2. Repulsion (Electron <-> Electron)
        repulsion = 0.0
        if n_electrons > 1:
            # Vectorized distance calculation
            diffs = config[:, None, :] - config[None, :, :]
            dists = np.linalg.norm(diffs, axis=2)
            
            # Use upper triangle only to avoid double counting and self-interaction
            # Extract upper triangle indices (k=1 excludes diagonal)
            tri_upper = np.triu_indices(n_electrons, k=1)
            valid_dists = dists[tri_upper]
            
            # Avoid division by zero (though lattice ensures distinct points)
            valid_dists = valid_dists[valid_dists > 0.001] 
            repulsion = np.sum(1.0 / valid_dists)

        return repulsion - attraction

    def find_ground_state(self, atomic_number: int, trials: int = 20, steps: int = 50) -> float:
        """
        Uses Stochastic Hill Climbing to find the minimum energy configuration
        for a given number of electrons (Z).
        """
        n_electrons = atomic_number
        nucleus_charge = atomic_number
        
        # Optimization: Only search closest nodes relevant to Z size
        search_limit = min(len(self.lattice), max(20, n_electrons * 4))
        search_space = self.lattice[:search_limit]

        best_global_energy = float('inf')

        for _ in range(trials):
            # 1. Random Initialization: Pick N random slots
            indices = np.random.choice(len(search_space), n_electrons, replace=False)
            current_config = search_space[indices].copy()
            current_energy = self._calculate_energy(current_config, nucleus_charge)

            # 2. Relaxation Loop (Shake)
            for _ in range(steps):
                # Pick a random electron to move
                e_idx = np.random.randint(n_electrons)
                old_pos = current_config[e_idx].copy()
                
                # Pick a random empty slot to move to
                target_idx = np.random.randint(len(search_space))
                target_pos = search_space[target_idx]

                # Check if occupied
                # (Simple check: is target_pos in current_config?)
                # For small arrays, this is fast enough.
                is_occupied = False
                for pos in current_config:
                    if np.array_equal(pos, target_pos):
                        is_occupied = True
                        break
                
                if not is_occupied:
                    # Move
                    current_config[e_idx] = target_pos
                    new_energy = self._calculate_energy(current_config, nucleus_charge)

                    # Greedy acceptance
                    if new_energy < current_energy:
                        current_energy = new_energy
                    else:
                        # Revert
                        current_config[e_idx] = old_pos

            if current_energy < best_global_energy:
                best_global_energy = current_energy

        return best_global_energy

    def run_periodic_table_scan(self, max_z: int = 20):
        """Runs the simulation for Z=1 to max_z and plots results."""
        results_z = []
        results_e = []

        print(f"--- Starting Scan (Z=1 to {max_z}) ---")
        for z in range(1, max_z + 1):
            energy = self.find_ground_state(z)
            results_z.append(z)
            results_e.append(energy)
            print(f"Z={z}: Energy={energy:.4f}")

        self._plot_results(results_z, results_e)

    def _plot_results(self, z_vals, e_vals):
        """Plots Energy per Electron to highlight stability peaks."""
        z_arr = np.array(z_vals)
        e_arr = np.array(e_vals)
        
        # Metric: Energy per Electron. Lower is more stable (tighter binding).
        # We look for local minima or distinct kinks.
        e_per_electron = e_arr / z_arr

        plt.figure(figsize=(12, 7))
        plt.plot(z_arr, e_per_electron, 'o-', color='cyan', linewidth=2, label='Energy per Electron')
        
        # Mark known Noble Gases (Magic Numbers)
        nobles = [2, 10, 18, 36]
        for n in nobles:
            if n <= max(z_arr):
                plt.axvline(x=n, color='red', linestyle='--', alpha=0.7)
                plt.text(n, np.min(e_per_electron), f" He/Ne/Ar\n (Z={n})", 
                         color='white', fontweight='bold', backgroundcolor='red', rotation=90)

        plt.title('Project Simureality: Geometric Emergence of Chemical Stability', fontsize=15)
        plt.xlabel('Atomic Number (Z)', fontsize=12)
        plt.ylabel('Energy / Z (Arbitrary Lattice Units)', fontsize=12)
        plt.grid(True, which='both', linestyle='--', alpha=0.3)
        plt.legend()
        
        # Invert Y axis because Lower Energy = More Stable
        plt.gca().invert_yaxis()
        
        # Style adjustments for "Hacker/Lab" look
        plt.style.use('dark_background')
        
        output_file = 'simureality_fcc_scan.png'
        plt.savefig(output_file, dpi=150)
        print(f"--- Scan Complete. Plot saved to {output_file} ---")
        plt.show()

if __name__ == "__main__":
    # Create simulator and run
    sim = LatticeChemistrySimulator(r_max=5)
    sim.run_periodic_table_scan(max_z=20)
