import numpy as np

# --- КОНСТАНТЫ SIMUREALITY ---
RYDBERG = 13.606
GAMMA_SYS = 1.0418

# --- GEOMETRIC ALPHABET (FULL) ---
geo_targets = {
    "0.00 (Dust)": 0.000, 
    "1/11 (Jam)": 1/11.0, "1/8 (Oct)": 0.125, "1/7 (Sept)": 1/7.0, 
    "1/6 (Hex)": 1/6.0, "1/5 (Pent)": 0.200, "1/4 (Tetra)": 0.250,
    "1/π (Tube)": 1/np.pi, "1/3 (Line)": 1/3.0, "1/e (Decay)": 1/np.e,
    "3/8 (Octant)": 3/8.0, "√2-1 (Void)": np.sqrt(2)-1, "1/√5 (Mag)": 1/np.sqrt(5),
    "1/2 (Half)": 0.500,
    "Rect (C=C)": 1 - 1/np.sqrt(5), 
    "φ-1 (Golden)": (np.sqrt(5)-1)/2,
    "2/π (Circle)": 2/np.pi, 
    "2/3 (Plane)": 2/3.0, 
    "1/√2 (Root)": 1/np.sqrt(2),
    "√φ (Ceramic)": np.sqrt((np.sqrt(5)-1)/2),
    "√2/3 (Glass)": np.sqrt(2/3),
    "9/10 (Super)": 0.900,
    "12/13 (MaxPack)": 12/13.0,
    "1.0 (Unity)": 1.000, "γ_sys (Tax)": GAMMA_SYS,
    "8/7 (SeptInv)": 8/7.0, "5/4 (Expand)": 1.250, "√2 (Diag)": np.sqrt(2)
}

# --- ATOMIC DATA (FIXED & EXPANDED) ---
atoms = {
    'H': {'n':1, 'ie':13.60}, 
    'Li':{'n':2, 'ie':5.39}, 'Be':{'n':2, 'ie':9.32}, 'B': {'n':2, 'ie':8.30},
    'C': {'n':2, 'ie':11.26}, 'N': {'n':2, 'ie':14.53}, 'O': {'n':2, 'ie':13.62},
    'F': {'n':2, 'ie':17.42}, 
    'Na':{'n':3, 'ie':5.14}, 'Mg':{'n':3, 'ie':7.65}, 'Al':{'n':3, 'ie':5.99},
    'Si':{'n':3, 'ie':8.15}, 'P': {'n':3, 'ie':10.49}, 'S': {'n':3, 'ie':10.36},
    'Cl':{'n':3, 'ie':12.97}, 
    'K': {'n':4, 'ie':4.34}, 'Ca':{'n':4, 'ie':6.11}, 'Sc':{'n':4, 'ie':6.54},
    'Ti':{'n':4, 'ie':6.82}, 'V':{'n':4, 'ie':6.74}, 'Cr':{'n':4, 'ie':6.77},
    'Mn':{'n':4, 'ie':7.43}, 'Fe':{'n':4, 'ie':7.90}, 'Co':{'n':4, 'ie':7.86},
    'Ni':{'n':4, 'ie':7.64}, 'Cu':{'n':4, 'ie':7.73}, 'Zn':{'n':4, 'ie':9.39},
    'Ga':{'n':4, 'ie':6.00}, 'Ge':{'n':4, 'ie':7.90}, 'As':{'n':4, 'ie':9.81},
    'Se':{'n':4, 'ie':9.75}, 'Br':{'n':4, 'ie':11.81},
    'Rb':{'n':5, 'ie':4.18}, 'Sr':{'n':5, 'ie':5.70}, 'Y':{'n':5, 'ie':6.38},
    'Zr':{'n':5, 'ie':6.84}, 'Nb':{'n':5, 'ie':6.88}, 'Mo':{'n':5, 'ie':7.09},
    'Sn':{'n':5, 'ie':7.34}, 'Sb':{'n':5, 'ie':8.64}, 'Te':{'n':5, 'ie':9.01},
    'I': {'n':5, 'ie':10.45},
    'Cs':{'n':6, 'ie':3.89}, 'Ba':{'n':6, 'ie':5.21}, 'La':{'n':6, 'ie':5.58},
    'Hf':{'n':6, 'ie':6.83}, 'Ta':{'n':6, 'ie':7.89}, 'W':{'n':6, 'ie':7.98},
    # Missing elements added below:
    'Pb':{'n':6, 'ie':7.42}, 'Au':{'n':6, 'ie':9.23}, 'Pt':{'n':6, 'ie':9.00},
    'Hg':{'n':6, 'ie':10.44}, 'Th':{'n':7, 'ie':6.31}, 'U': {'n':7, 'ie':6.19}
}

# --- DATABASE: ~200 SPECIFIC BONDS ---
full_structure_db = [
    # --- 1. HYDROCARBONS ---
    ('Methane (CH4)', [('C', 'H', 4.52, 'sp3-s')]),
    ('Ethane (C2H6)', [('C', 'C', 3.82, 'sp3-sp3'), ('C', 'H', 4.28, 'primary')]),
    ('Propane (C3H8)', [('C', 'C', 3.75, 'sp3-sp3'), ('C', 'H', 4.25, 'secondary')]),
    ('Butane (C4H10)', [('C', 'C', 3.70, 'internal'), ('C', 'H', 4.15, 'tertiary')]),
    ('Ethene (C2H4)', [('C', 'C', 7.50, 'double'), ('C', 'H', 4.75, 'sp2-s')]),
    ('Ethyne (C2H2)', [('C', 'C', 9.90, 'triple'), ('C', 'H', 5.70, 'sp-s')]),
    ('Benzene (C6H6)', [('C', 'C', 5.35, 'aromatic'), ('C', 'H', 4.85, 'aryl')]),
    ('Toluene (C7H8)', [('C', 'C', 4.40, 'Me-Ph'), ('C', 'H', 3.90, 'benzyl')]),

    # --- 2. ALCOHOLS & ETHERS ---
    ('Methanol (CH3OH)', [('C', 'O', 3.94, 'primary'), ('O', 'H', 4.50, 'hydroxyl'), ('C', 'H', 4.10, 'alpha')]),
    ('Ethanol (C2H5OH)', [('C', 'C', 3.65, 'single'), ('C', 'O', 4.00, 'primary'), ('O', 'H', 4.55, 'hydroxyl')]),
    ('Isopropanol', [('C', 'O', 4.05, 'secondary'), ('O', 'H', 4.60, 'hydroxyl')]),
    ('DME (Ether)', [('C', 'O', 3.75, 'ether-link'), ('C', 'H', 4.15, 'ether-H')]),
    ('Phenol (PhOH)', [('C', 'O', 4.85, 'aryl-O'), ('O', 'H', 3.90, 'acidic')]),

    # --- 3. CARBONYLS ---
    ('Formaldehyde', [('C', 'O', 7.70, 'carbonyl'), ('C', 'H', 3.80, 'formyl')]),
    ('Acetaldehyde', [('C', 'C', 3.60, 'alpha-C'), ('C', 'O', 7.90, 'carbonyl'), ('C', 'H', 3.75, 'ald-H')]),
    ('Acetone', [('C', 'C', 3.55, 'beta-C'), ('C', 'O', 8.05, 'ketone')]),
    ('Formic Acid', [('C', 'O', 8.40, 'double'), ('C', 'O', 3.90, 'single'), ('O', 'H', 4.80, 'acid')]),
    ('Acetic Acid', [('C', 'C', 3.65, 'C-C'), ('C', 'O', 8.30, 'C=O'), ('C', 'O', 4.00, 'C-OH')]),
    ('CO2', [('C', 'O', 8.32, 'linear-1'), ('C', 'O', 8.32, 'linear-2')]),
    ('CO', [('C', 'O', 11.16, 'triple-like')]),

    # --- 4. NITROGEN COMPOUNDS ---
    ('Methylamine', [('C', 'N', 3.45, 'amine'), ('N', 'H', 4.05, 'amino'), ('C', 'H', 4.00, 'alpha')]),
    ('Aniline', [('C', 'N', 4.40, 'aryl-N'), ('N', 'H', 4.10, 'amino-ph')]),
    ('HCN', [('C', 'N', 9.70, 'triple'), ('C', 'H', 5.40, 'acidic')]),
    ('Acetonitrile', [('C', 'C', 5.20, 'C-CN'), ('C', 'N', 9.50, 'C#N')]),
    ('Hydrazine', [('N', 'N', 2.85, 'single'), ('N', 'H', 4.15, 'hydrazyl')]),
    ('N2', [('N', 'N', 9.80, 'triple')]),

    # --- 5. HALIDES ---
    ('Methyl Fluoride', [('C', 'F', 4.90, 'C-F'), ('C', 'H', 4.30, 'alpha')]),
    ('Methyl Chloride', [('C', 'Cl', 3.60, 'C-Cl'), ('C', 'H', 4.20, 'alpha')]),
    ('Methyl Bromide', [('C', 'Br', 3.00, 'C-Br'), ('C', 'H', 4.25, 'alpha')]),
    ('Methyl Iodide', [('C', 'I', 2.50, 'C-I'), ('C', 'H', 4.30, 'alpha')]),
    ('CF4', [('C', 'F', 5.60, 'tetra-F')]),
    ('CCl4', [('C', 'Cl', 3.40, 'tetra-Cl')]),
    ('Chloroform', [('C', 'Cl', 3.30, 'tri-Cl'), ('C', 'H', 4.00, 'acidic')]),
    ('Ph-Cl', [('C', 'Cl', 4.10, 'aryl-Cl')]),

    # --- 6. SILICON & PHOSPHORUS ---
    ('Silane (SiH4)', [('Si', 'H', 3.30, 'Si-H')]),
    ('Disilane (Si2H6)', [('Si', 'Si', 3.20, 'Si-Si'), ('Si', 'H', 3.35, 'Si-H')]),
    ('SiF4', [('Si', 'F', 6.10, 'Si-F')]),
    ('SiCl4', [('Si', 'Cl', 4.10, 'Si-Cl')]),
    ('SiC', [('Si', 'C', 4.60, 'lattice')]),
    ('SiO2', [('Si', 'O', 8.30, 'lattice')]),
    ('Phosphine', [('P', 'H', 3.50, 'P-H')]),
    ('PCl3', [('P', 'Cl', 3.35, 'P-Cl')]),
    ('POCl3', [('P', 'O', 6.10, 'P=O'), ('P', 'Cl', 3.40, 'P-Cl')]),

    # --- 7. SULFUR COMPOUNDS ---
    ('H2S', [('S', 'H', 3.90, 'S-H')]),
    ('Methanethiol', [('C', 'S', 3.10, 'C-S'), ('S', 'H', 3.80, 'S-H')]),
    ('CS2', [('C', 'S', 7.40, 'double')]),
    ('SF6', [('S', 'F', 3.50, 'hyperval')]),
    ('SO2', [('S', 'O', 5.60, 'resonant')]),
    ('SO3', [('S', 'O', 4.80, 'resonant')]),

    # --- 8. DIATOMICS ---
    ('H2', [('H', 'H', 4.52, 'sigma')]),
    ('F2', [('F', 'F', 1.60, 'repulsion')]),
    ('Cl2', [('Cl', 'Cl', 2.50, 'single')]),
    ('Br2', [('Br', 'Br', 2.00, 'single')]),
    ('I2', [('I', 'I', 1.57, 'single')]),
    ('O2', [('O', 'O', 5.15, 'double')]),
    ('HCl', [('H', 'Cl', 4.43, 'polar')]),
    ('HBr', [('H', 'Br', 3.75, 'polar')]),
    ('HI', [('H', 'I', 3.06, 'polar')]),
    ('NO', [('N', 'O', 6.50, 'radical')]),

    # --- 9. TRANSITION METALS ---
    ('TiO2', [('Ti', 'O', 6.90, 'lattice')]),
    ('ZrO2', [('Zr', 'O', 7.90, 'lattice')]),
    ('HfO2', [('Hf', 'O', 8.30, 'lattice')]),
    ('Ta2O5', [('Ta', 'O', 8.10, 'lattice')]),
    ('TiN', [('Ti', 'N', 5.00, 'ceramic')]),
    ('ZrN', [('Zr', 'N', 5.90, 'ceramic')]),
    ('VN', [('V', 'N', 4.90, 'ceramic')]),
    
    # --- 10. BORON & ALUMINUM ---
    ('BF3', [('B', 'F', 6.50, 'strong')]),
    ('BCl3', [('B', 'Cl', 4.60, 'lewis')]),
    ('AlCl3', [('Al', 'Cl', 4.40, 'dimer')]),
    ('Al2O3', [('Al', 'O', 5.30, 'lattice')]),
    ('BN', [('B', 'N', 4.10, 'layer')]),

    # --- 11. HEAVY & EXOTIC (ADDED FIX) ---
    ('SnH4', [('Sn', 'H', 2.70, 'weak')]),
    ('PbH4', [('Pb', 'H', 2.10, 'unstable')]),
    ('ThO2', [('Th', 'O', 9.10, 'nuclear')]),
    ('UO2', [('U', 'O', 7.80, 'nuclear')]),
    ('La2O3', [('La', 'O', 8.20, 'lanthanide')]),
    ('Au-Cl', [('Au', 'Cl', 3.30, 'noble')]),
    ('Pt-C', [('Pt', 'C', 6.20, 'surface')])
]

def get_z_eff(atom_sym):
    if atom_sym not in atoms:
        # Fallback to avoid crash, but warn
        print(f"Warning: Missing atom {atom_sym}")
        return 1.0
    data = atoms[atom_sym]
    return data['n'] * np.sqrt(data['ie'] / RYDBERG)

def analyze_deep_structure():
    print(f"{'Structure':<20} | {'Bond':<10} | {'Type':<10} | {'BDE':<6} | {'Fact':<6} | {'Diff':<6} | {'Match'}")
    print("=" * 95)
    
    total_bonds = 0
    matches = 0
    tolerance = 0.045 # 4.5% natural lattice noise
    
    for mol_name, bonds in full_structure_db:
        for a1, a2, energy, b_type in bonds:
            total_bonds += 1
            
            z1 = get_z_eff(a1); z2 = get_z_eff(a2)
            # Use 'get' to safely access 'n' with fallback
            n1 = atoms.get(a1, {'n':1})['n']
            n2 = atoms.get(a2, {'n':1})['n']
            
            n_avg = (n1 + n2) / 2.0
            e_base = RYDBERG * (z1 * z2) / (n_avg**2)
            
            factor = energy / e_base
            
            best_diff = 100.0
            best_match = "???"
            
            for gname, gval in geo_targets.items():
                diff = abs(factor - gval)
                if diff < best_diff:
                    best_diff = diff
                    best_match = gname
            
            status = "+" if best_diff < tolerance else "!"
            if status == "+": matches += 1
            
            pair = f"{a1}-{a2}"
            print(f"{mol_name[:19]:<20} | {pair:<10} | {b_type:<10} | {energy:<6.2f} | {factor:<6.3f} | {best_diff:.3f} | {status} {best_match}")
            
    print("=" * 95)
    print(f"FINAL SCORE: {matches}/{total_bonds} matches ({matches/total_bonds*100:.1f}%)")

if __name__ == "__main__":
    analyze_deep_structure()
