import numpy as np
import random

# --- Simureality Hardware Constants ---
GAMMA = 3.325
SYS_TAX = 1.0418 # Impedance penalty for G/C bases
R_DNA = 10.0     # Helix radius proxy
TWIST = np.radians(34.3)
RISE = 3.4

# DNA Vector Dictionary
ISA_DNA = {
    'A': np.array([RISE, R_DNA * np.sin(TWIST), R_DNA * np.cos(TWIST)]),
    'T': np.array([RISE, R_DNA * np.sin(-TWIST), R_DNA * np.cos(-TWIST)]),
    # G and C trigger the System Tax, stretching the vector
    'G': np.array([RISE * SYS_TAX, R_DNA * np.sin(TWIST*1.2), R_DNA * np.cos(TWIST*1.2)]),
    'C': np.array([RISE * SYS_TAX, R_DNA * np.sin(-TWIST*1.2), R_DNA * np.cos(-TWIST*1.2)])
}
BASES = ['A', 'T', 'G', 'C']

def get_intron_fitness(sequence):
    current_pos = np.array([0.0, 0.0, 0.0])
    lags = []
    
    for base in sequence:
        current_pos += ISA_DNA[base]
        # Calculate lag: distance to the nearest perfect node
        nearest_node = np.round(current_pos / GAMMA) * GAMMA
        node_lag = np.linalg.norm(current_pos - nearest_node)
        lags.append(node_lag)
    
    # Final miss: how far off is the port alignment for the next Exon?
    final_node = np.round(current_pos / GAMMA) * GAMMA
    final_miss = np.linalg.norm(current_pos - final_node)
    
    # Fitness prioritizes zero-lag at the exact junction
    fitness = 1.0 / (final_miss * 10 + np.sum(np.array(lags)**2) + 0.0001)
    return fitness, final_miss, sum(lags)

def mutate_intron(sequence):
    mut_type = random.choice(['swap', 'add', 'remove'])
    seq = list(sequence)
    if mut_type == 'swap' and len(seq) > 0:
        seq[random.randint(0, len(seq)-1)] = random.choice(BASES)
    elif mut_type == 'add' and len(seq) < 50:
        seq.insert(random.randint(0, len(seq)), random.choice(BASES))
    elif mut_type == 'remove' and len(seq) > 10:
        seq.pop(random.randint(0, len(seq)-1))
    return "".join(seq)

# --- Exon-Intron Calibration Core ---
print("BOOTING INTRON CALIBRATOR (BIO-COMPILER)...")
POP_SIZE = 100
GENERATIONS = 300
population = ["".join(random.choices(BASES, k=20)) for _ in range(POP_SIZE)]

for gen in range(GENERATIONS):
    scored = [(get_intron_fitness(seq), seq) for seq in population]
    scored.sort(key=lambda x: x[0][0], reverse=True)
    
    if gen % 50 == 0 or scored[0][0][1] < 0.1:
        metrics, best_seq = scored[0]
        fitness, final_miss, total_lag = metrics
        print(f"Gen {gen:03d} | Miss: {final_miss:.4f} | Total Lag: {total_lag:.2f} | Len: {len(best_seq)}")
        if final_miss < 0.1:
            print(f">>> HARDWARE SYNC ACHIEVED. DELAY LINE CALIBRATED.\n>>> INTRON SEQUENCE: {best_seq}")
            break
            
    survivors = [seq for score, seq in scored[:POP_SIZE//4]]
    population = survivors[:]
    while len(population) < POP_SIZE:
        population.append(mutate_intron(random.choice(survivors)))
