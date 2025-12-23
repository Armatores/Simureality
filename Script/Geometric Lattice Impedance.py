import pandas as pd
import numpy as np

def simureality_github_release():
    print(f"{'='*100}")
    print(f" SIMUREALITY PROTOCOL: GEOMETRIC LATTICE IMPEDANCE (v1.0)")
    print(f" Abstract: Ab-initio calculation of Electronic Work Function based on")
    print(f"           Lattice Geometry, Yield Strength (Plasticity), and Oxide Topology (P-B Ratio).")
    print(f"{'='*100}")

    # --- 1. FUNDAMENTAL CONSTANTS ---
    CONST_FCC = 1 / ((1 + np.sqrt(5))/2)  # 0.618 (Golden Ratio Projection)
    CONST_BCC = 1 / np.sqrt(3)            # 0.577 (Cubic Diagonal Projection)
    
    GAMMA_SYS = 1.0418       # System Instantiation Tax (Derived from Vacuum Impedance)
    IDEAL_HCP_CA = 1.633     # Ideal c/a ratio for hexagonal packing
    
    # --- 2. PHYSICAL PARAMETERS ---
    K_PLAST = 2.4            # Plasticity Coupling Coefficient
    HCP_MISMATCH = 0.15      # Topological Penalty (HCP vs FCC Vacuum)
    YIELD_THRESHOLD = 190    # MPa (Threshold for lattice topological stability)

    # --- 3. DATASET (38 Elements) ---
    # Type: 'ARMOR' (Pilling-Bedworth > 1), 'NORMAL' (Standard Lattice)
    data = [
        # === S-BLOCK (Soft / Alkaline) ===
        {'El': 'Li', 'St':'BCC', 'Ion':5.39, 'WF':2.90, 'Yield':15,  'CA':0,    'Type':'NORMAL', 'Group':'Alkali'},
        {'El': 'Na', 'St':'BCC', 'Ion':5.14, 'WF':2.36, 'Yield':5,   'CA':0,    'Type':'NORMAL', 'Group':'Alkali'},
        {'El': 'Mg', 'St':'HCP', 'Ion':7.65, 'WF':3.66, 'Yield':90,  'CA':1.62, 'Type':'NORMAL', 'Group':'Alkaline Earth'},
        {'El': 'Ca', 'St':'FCC', 'Ion':6.11, 'WF':2.87, 'Yield':12,  'CA':0,    'Type':'NORMAL', 'Group':'Alkaline Earth'},
        {'El': 'Sr', 'St':'FCC', 'Ion':5.69, 'WF':2.59, 'Yield':8,   'CA':0,    'Type':'NORMAL', 'Group':'Alkaline Earth'},
        {'El': 'Ba', 'St':'BCC', 'Ion':5.21, 'WF':2.70, 'Yield':6,   'CA':0,    'Type':'NORMAL', 'Group':'Alkaline Earth'},
        {'El': 'Be', 'St':'HCP', 'Ion':9.32, 'WF':4.98, 'Yield':240, 'CA':1.56, 'Type':'NORMAL', 'Group':'Alkaline Earth'},

        # === P-BLOCK (Protective Oxide Armor) ===
        {'El': 'Al', 'St':'FCC',  'Ion':5.99, 'WF':4.28, 'Yield':30,  'CA':0,    'Type':'ARMOR',  'Group':'Post-Transition', 'Val':3}, 
        {'El': 'Ga', 'St':'Orth', 'Ion':6.00, 'WF':4.20, 'Yield':10,  'CA':0,    'Type':'ARMOR',  'Group':'Post-Transition', 'Val':3},

        # === TRANSITION METALS (The Rigid Backbone) ===
        {'El': 'Sc', 'St':'HCP', 'Ion':6.54, 'WF':3.50, 'Yield':150, 'CA':1.59,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ti', 'St':'HCP', 'Ion':6.82, 'WF':4.33, 'Yield':350, 'CA':1.58,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'V',  'St':'BCC', 'Ion':6.74, 'WF':4.30, 'Yield':200, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Cr', 'St':'BCC', 'Ion':6.77, 'WF':4.50, 'Yield':360, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Mn', 'St':'BCC', 'Ion':7.43, 'WF':4.10, 'Yield':250, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Fe', 'St':'BCC', 'Ion':7.90, 'WF':4.50, 'Yield':250, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Co', 'St':'HCP', 'Ion':7.88, 'WF':5.00, 'Yield':220, 'CA':1.62,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ni', 'St':'FCC', 'Ion':7.64, 'WF':5.15, 'Yield':150, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Cu', 'St':'FCC', 'Ion':7.73, 'WF':4.65, 'Yield':70,  'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Zn', 'St':'HCP', 'Ion':9.39, 'WF':4.33, 'Yield':100, 'CA':1.856, 'Type':'NORMAL', 'Group':'Transition'},

        {'El': 'Y',  'St':'HCP', 'Ion':6.22, 'WF':3.10, 'Yield':40,  'CA':1.57,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Zr', 'St':'HCP', 'Ion':6.63, 'WF':4.05, 'Yield':250, 'CA':1.59,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Nb', 'St':'BCC', 'Ion':6.76, 'WF':4.30, 'Yield':210, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Mo', 'St':'BCC', 'Ion':7.09, 'WF':4.60, 'Yield':450, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Tc', 'St':'HCP', 'Ion':7.28, 'WF':4.70, 'Yield':300, 'CA':1.60,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ru', 'St':'HCP', 'Ion':7.36, 'WF':4.71, 'Yield':400, 'CA':1.58,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Rh', 'St':'FCC', 'Ion':7.46, 'WF':4.98, 'Yield':200, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Pd', 'St':'FCC', 'Ion':8.34, 'WF':5.12, 'Yield':500, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ag', 'St':'FCC', 'Ion':7.58, 'WF':4.26, 'Yield':15,  'CA':0,     'Type':'NORMAL', 'Group':'Noble/Soft'},
        {'El': 'Cd', 'St':'HCP', 'Ion':8.99, 'WF':4.22, 'Yield':30,  'CA':1.886, 'Type':'NORMAL', 'Group':'Transition'},

        {'El': 'Hf', 'St':'HCP', 'Ion':6.83, 'WF':3.90, 'Yield':200, 'CA':1.58,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ta', 'St':'BCC', 'Ion':7.55, 'WF':4.25, 'Yield':180, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'W',  'St':'BCC', 'Ion':7.86, 'WF':4.55, 'Yield':750, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Re', 'St':'HCP', 'Ion':7.83, 'WF':4.96, 'Yield':400, 'CA':1.61,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Os', 'St':'HCP', 'Ion':8.44, 'WF':5.83, 'Yield':1000,'CA':1.58,  'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Ir', 'St':'FCC', 'Ion':8.97, 'WF':5.27, 'Yield':300, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Pt', 'St':'FCC', 'Ion':8.96, 'WF':5.65, 'Yield':140, 'CA':0,     'Type':'NORMAL', 'Group':'Transition'},
        {'El': 'Au', 'St':'FCC', 'Ion':9.22, 'WF':5.10, 'Yield':20,  'CA':0,     'Type':'NORMAL', 'Group':'Noble/Soft'},

        # === POST-TRANSITION (Others) ===
        {'El': 'Sn', 'St':'Tetra','Ion':7.34,'WF':4.42, 'Yield':15,  'CA':0,     'Type':'NORMAL', 'Group':'Post-Transition'},
        {'El': 'Pb', 'St':'FCC', 'Ion':7.42, 'WF':4.25, 'Yield':10,  'CA':0,     'Type':'NORMAL', 'Group':'Post-Transition'},
    ]
    df = pd.DataFrame(data)

    # --- 4. COMPUTATIONAL ENGINE ---
    
    # A. Geometric Baseline
    df['Geo_Factor'] = np.where(df['St'] == 'BCC', CONST_BCC, CONST_FCC)
    df['WF_Ideal'] = df['Ion'] * df['Geo_Factor']

    # B. Correction Factors
    
    # 1. Plasticity Tax (Loss = K / Yield). 
    #    Applies to all NORMAL metals. Caps at 25% to avoid singularities.
    df['Loss_Plast'] = (K_PLAST / df['Yield']).clip(upper=0.25)
    
    # 2. Topology Mismatch (HCP vs FCC Vacuum).
    #    Applies only if Yield < Threshold (lattice cannot sustain the stress).
    df['Loss_Topo'] = np.where(
        (df['St'] == 'HCP') & (df['Yield'] < YIELD_THRESHOLD), 
        HCP_MISMATCH, 
        0.0
    )

    # 3. Distortion Penalty (c/a ratio mismatch).
    #    Applies if lattice is stretched/squashed beyond ideal HCP (1.633).
    df['Distort_Ratio'] = np.where(df['CA'] > 0, abs(df['CA'] - IDEAL_HCP_CA) / IDEAL_HCP_CA, 0.0)
    df['Loss_Distort'] = np.where(df['Distort_Ratio'] > 0.05, df['Distort_Ratio'], 0.0)

    # 4. Armor Boost (Pilling-Bedworth).
    #    Applies only to ARMOR types (Al, Ga).
    df['Boost_Armor'] = np.where(df['Type'] == 'ARMOR', GAMMA_SYS ** df['Val'], 1.0)

    # C. Final Prediction
    df['WF_Pred'] = np.where(
        df['Type'] == 'ARMOR',
        df['WF_Ideal'] * df['Boost_Armor'],
        df['WF_Ideal'] * (1 - df['Loss_Plast'] - df['Loss_Topo'] - df['Loss_Distort'])
    )

    df['Error'] = abs(df['WF_Pred'] - df['WF']) / df['WF'] * 100

    # --- 5. REPORT GENERATION ---
    print(f"{'El':<3} {'St':<5} | {'Real':<5} {'Pred':<5} | {'Error %':<7} | {'Correction Applied'}")
    print("-" * 80)
    
    for i, row in df.iterrows():
        fixes = []
        if row['Boost_Armor'] > 1.0: fixes.append("ARMOR")
        if row['Loss_Plast'] > 0.05: fixes.append("YIELD")
        if row['Loss_Topo'] > 0.0: fixes.append("TOPO")
        if row['Loss_Distort'] > 0.0: fixes.append("DIST")
        if not fixes: fixes.append("PURE")
        
        star = "★" if row['Error'] < 2.0 else ""
        print(f"{row['El']:<3} {row['St']:<5} | {row['WF']:<5.2f} {row['WF_Pred']:<5.2f} | {row['Error']:<7.1f} | {'+'.join(fixes)} {star}")

    print("-" * 80)
    print(" SUMMARY BY GROUP:")
    print("-" * 80)
    
    groups = df['Group'].unique()
    for g in groups:
        subset = df[df['Group'] == g]
        avg_err = subset['Error'].mean()
        print(f" > {g:<16}: {avg_err:.2f}% (N={len(subset)})")

    print("-" * 80)
    print(f" GLOBAL AVERAGE ERROR: {df['Error'].mean():.2f}%")
    print(f"{'='*100}")

if __name__ == "__main__":
    simureality_github_release()
