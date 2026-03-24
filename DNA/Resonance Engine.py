import numpy as np
import random

# --- Simureality Hardware Constants ---
GAMMA = 3.325 # FCC Lattice port step (Å)
ENVIRONMENT_KEY = np.array([6.0, 5.0, 4.0]) # Target phase coordinate
MAX_GENE_LEN = 30
POP_SIZE = 200
GENERATIONS = 500

# Instruction Set Architecture (Vacuum Vectors)
ISA_VECTORS = {
    'STRUCT': np.array([1.0, 0.0, 0.0]), # Linear bus extension
    'LOGIC':  np.array([0.5, 0.5, 0.0]), # Resonance gate
    'JUMP':   np.array([0.0, 0.5, 0.5]), # Phase bend
    'LOCK':   np.array([0.5, 0.0, 0.5])  # Hardware jumper
}
OPCODES = list(ISA_VECTORS.keys())

def get_resonance_metrics(sequence):
    token = np.array([0.0, 0.0, 0.0])
    for op in sequence: 
        token += ISA_VECTORS[op]
    
    # Interference is the metric distance to the Environment Key
    interference = np.linalg.norm(ENVIRONMENT_KEY - token)
    
    # Fitness maximizes resonance while penalizing excessive length (Occam's Razor)
    fitness = 1.0 / (interference + (len(sequence) * 0.005) + 0.0001)
    return fitness, interference, token

def mutate(sequence):
    if len(sequence) == 0: return [random.choice(OPCODES)]
    mut_type = random.choice(['add', 'remove', 'swap'])
    new_seq = sequence[:]
    
    if mut_type == 'add' and len(new_seq) < MAX_GENE_LEN:
        new_seq.insert(random.randint(0, len(new_seq)), random.choice(OPCODES))
    elif mut_type == 'remove' and len(new_seq) > 1:
        new_seq.pop(random.randint(0, len(new_seq)-1))
    elif mut_type == 'swap':
        new_seq[random.randint(0, len(new_seq)-1)] = random.choice(OPCODES)
    return new_seq

# --- Execution Core ---
print("BOOTING RESONANCE ENGINE...")
population = [[random.choice(OPCODES) for _ in range(random.randint(5, 15))] for _ in range(POP_SIZE)]

for gen in range(GENERATIONS):
    scored = [(get_resonance_metrics(seq), seq) for seq in population]
    scored.sort(key=lambda x: x[0][0], reverse=True)
    
    if gen % 100 == 0 or scored[0][0][1] < 0.01:
        best_fit, best_inter, best_token = scored[0][0]
        print(f"Gen {gen:03d} | Miss: {best_inter:.4f} | Len: {len(scored[0][1])} | Token: {best_token}")
        if best_inter < 0.01:
            print(">>> PERFECT RESONANCE ACHIEVED. STOP-CODON TRIGGERED.")
            break
            
    # Simple selection and reproduction
    survivors = [seq for score, seq in scored[:POP_SIZE//4]]
    population = survivors[:]
    while len(population) < POP_SIZE:
        population.append(mutate(random.choice(survivors)))
