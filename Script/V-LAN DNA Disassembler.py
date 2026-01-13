import numpy as np

# --- 1. SYSTEM CLOCK (The Power Rail) ---
# Energy of the Phosphate Backbone Link (P-O bond in DNA/RNA)
# From Viral Script / Literature: ~5.90 - 6.00 eV
CLOCK_RATE_DNA = 6.00  # eV (Reference Voltage)

# --- 2. GEOMETRIC INSTRUCTION SET (SIS) ---
# Logic Gates defined by Simureality
ops = {
    "NULL (0)":       0.000,
    "BIT_0 (1/10)":   0.100,      # Decimal divide
    "BIT_1 (1/6)":    1/6.0,      # Hex code (0.166)
    "BIT_2 (1/5)":    0.200,      # Pent code (0.200) - 5-fold symmetry
    "BIT_3 (1/4)":    0.250,      # Tetra code (0.250)
    "BIT_4 (1/3)":    1/3.0,      # Line code (0.333)
    "EXEC (1/2)":     0.500,      # Half / Execute
    "LOOP (1/π)":     1/np.pi,    # Infinite Loop (0.318)
    "GOLD (φ-1)":     (np.sqrt(5)-1)/2  # Golden Ratio (0.618)
}

# --- 3. DNA/RNA DATA PACKETS ---
# Source: Gas Phase Pairing Energies (Hobza et al., Sponer et al.)
# These are the "Values" of the genetic letters.
dna_packet = [
    # --- The Logical Pairs (Horizontal Code) ---
    # Adenine-Thymine (2 H-bonds)
    ('A-T Pair (DNA)', 0.62, 'Instruction: WEAK LOCK'),
    
    # Guanine-Cytosine (3 H-bonds)
    ('G-C Pair (DNA)', 1.18, 'Instruction: STRONG LOCK'),
    
    # Uracil Pair (RNA only)
    ('A-U Pair (RNA)', 0.58, 'Instruction: TEMP LOCK'),
    
    # --- The Stacking Interactions (Vertical Code) ---
    # How letters stick to each other vertically
    ('A-A Stack',      0.32, 'Vertical: READ NEXT'),
    ('G-G Stack',      0.58, 'Vertical: BLOCK'),
    
    # --- Errors / Mutations (Wobble Pairs) ---
    ('G-T Wobble',     0.45, 'Error: MISMATCH'),
    ('A-C Mismatch',   0.35, 'Error: INVALID OP')
]

def decode_dna():
    print(f"{'Opcode (Pair)':<15} | {'Energy':<6} | {'Ratio':<6} | {'Diff':<6} | {'Instruction'}")
    print("=" * 80)
    
    matches = 0
    total = len(dna_packet)
    # Tolerance is relative to the Clock Rate (Grid Noise)
    tolerance = 0.025 
    
    for name, energy, desc in dna_packet:
        # THE HACK: We divide Pair Energy by the Backbone Energy
        # Logic: The letters are fractions of the rail.
        ratio = energy / CLOCK_RATE_DNA
        
        best_diff = 100.0
        best_op = "???"
        
        for op_name, op_val in ops.items():
            diff = abs(ratio - op_val)
            if diff < best_diff:
                best_diff = diff
                best_op = op_name
        
        status = "[OK]" if best_diff < tolerance else "[!!]"
        if status == "[OK]": matches += 1
        
        print(f"{name:<15} | {energy:<6.2f} | {ratio:<6.3f} | {best_diff:.3f} | {status} {best_op}")
        
    print("=" * 80)
    print(f"DECRYPTION STATUS: {matches}/{total} opcodes recognized.")
    print("Simureality Genetic Disassembler v1.0")

if __name__ == "__main__":
    decode_dna()
