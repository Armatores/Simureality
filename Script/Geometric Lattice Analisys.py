import pandas as pd
import numpy as np

def simureality_v12_system_auditor():
    print(f"{'='*100}")
    print(f" SIMUREALITY V12: SYSTEM QUALITY AUDIT")
    print(f" OBJECTIVE: Compare 'Real Energy Deficit' vs 'Predicted Entropy Cost'")
    print(f"{'='*100}")

    # --- CONSTANTS ---
    CONST_FCC = 1 / ((1 + np.sqrt(5))/2)  # 0.618
    CONST_BCC = 1 / np.sqrt(3)            # 0.577
    
    # PARAMETERS
    VOL_THRESHOLD = 12.0
    STABILITY_THRESHOLD = 200
    IDEAL_HCP_CA = 1.633
    K_PLAST = 2.4

    # --- DATASET ---
    data = [
        # === REFERENCE (STABLE) ===
        {'El': 'W',  'St':'BCC', 'Ion':7.86, 'WF':4.55, 'Yield':750, 'Vol':9.53, 'CA':0,    'Type':'REF'},
        {'El': 'Fe', 'St':'BCC', 'Ion':7.90, 'WF':4.50, 'Yield':250, 'Vol':7.09, 'CA':0,    'Type':'REF'},
        
        # === PLASTICITY CHECK (Soft) ===
        {'El': 'Au', 'St':'FCC', 'Ion':9.22, 'WF':5.10, 'Yield':20,  'Vol':10.2, 'CA':0,    'Type':'SOFT'},
        {'El': 'Ag', 'St':'FCC', 'Ion':7.58, 'WF':4.26, 'Yield':15,  'Vol':10.2, 'CA':0,    'Type':'SOFT'},

        # === DENSITY CHECK (Fluffy) ===
        {'El': 'Ca', 'St':'FCC', 'Ion':6.11, 'WF':2.87, 'Yield':12,  'Vol':26.2, 'CA':0,    'Type':'FLUFFY'},
        {'El': 'Sr', 'St':'FCC', 'Ion':5.69, 'WF':2.59, 'Yield':8,   'Vol':33.9, 'CA':0,    'Type':'FLUFFY'},
        {'El': 'Ba', 'St':'BCC', 'Ion':5.21, 'WF':2.70, 'Yield':6,   'Vol':38.2, 'CA':0,    'Type':'FLUFFY'},

        # === DISTORTION CHECK (Noisy) ===
        {'El': 'Zn', 'St':'HCP', 'Ion':9.39, 'WF':4.33, 'Yield':100, 'Vol':9.16, 'CA':1.856,'Type':'NOISY'},
        {'El': 'Cd', 'St':'HCP', 'Ion':8.99, 'WF':4.22, 'Yield':30,  'Vol':13.0, 'CA':1.886,'Type':'NOISY'},

        # === ARMOR CHECK (Boosted) ===
        {'El': 'Al', 'St':'FCC', 'Ion':5.99, 'WF':4.28, 'Yield':30,  'Vol':10.0, 'CA':0,    'Type':'ARMOR'},
        {'El': 'Ga', 'St':'Orth','Ion':6.00, 'WF':4.20, 'Yield':10,  'Vol':11.8, 'CA':0,    'Type':'ARMOR'},
    ]
    df = pd.DataFrame(data)

    # --- CALCULATIONS ---

    # 1. IDEAL GEOMETRIC ENERGY (The Plan)
    df['Geo_Factor'] = np.where(df['St'] == 'BCC', CONST_BCC, CONST_FCC)
    df['E_Ideal'] = df['Ion'] * df['Geo_Factor']

    # 2. REAL DEFICIT (The Reality Check)
    # Сколько энергии реально пропало? (Если отрицательно - значит энергии прибыло)
    df['Deficit_Real'] = df['E_Ideal'] - df['WF']

    # 3. PREDICTED COST (The Model)
    
    # Cost 1: Plasticity (eV loss)
    # Loss fraction = (2.4/Yield) -> eV loss = E_Ideal * fraction
    df['Cost_Plast'] = np.where(
        (df['Yield'] < STABILITY_THRESHOLD) & (df['Type'] != 'ARMOR'),
        df['E_Ideal'] * (2.4 / df['Yield']).clip(upper=0.35),
        0.0
    )

    # Cost 2: Density (eV loss)
    # Loss fraction = 1 - (12/Vol)^0.35
    df['Cost_Dens'] = np.where(
        df['Vol'] > VOL_THRESHOLD,
        df['E_Ideal'] * (1 - ((VOL_THRESHOLD / df['Vol']) ** 0.35)),
        0.0
    )

    # Cost 3: Noise (eV loss)
    df['Distort'] = np.where(df['CA'] > 0, df['CA']/IDEAL_HCP_CA, 1.0)
    df['Cost_Noise'] = np.where(
        df['Distort'] > 1.05,
        df['E_Ideal'] * (1 - (1 / df['Distort']**2)),
        0.0
    )

    # Cost 4: Armor (Negative Cost = Gain)
    # Gain = E_Ideal * (1.04^3 - 1)
    df['Cost_Armor'] = np.where(
        df['Type'] == 'ARMOR',
        -1 * df['E_Ideal'] * ((1.0418**3) - 1), 
        0.0
    )

    # TOTAL PREDICTED COST
    df['Deficit_Pred'] = df['Cost_Plast'] + df['Cost_Dens'] + df['Cost_Noise'] + df['Cost_Armor']

    # --- SYSTEM QUALITY INDEX (Q) ---
    df['Q_Index'] = df['WF'] / df['E_Ideal']

    # --- AUDIT ---
    # Does the predicted deficit match the real deficit?
    df['Audit_Diff'] = abs(df['Deficit_Pred'] - df['Deficit_Real'])

    # --- OUTPUT ---
    print(f"{'El':<3} {'Q-Ind':<6} | {'Ideal':<5} {'Real':<5} | {'LOST(Real)':<10} {'LOST(Pred)':<10} | {'Audit'}")
    print("-" * 100)

    for i, row in df.iterrows():
        # Quality Label
        q_lbl = ""
        if row['Q_Index'] > 1.05: q_lbl = "[SUPER]" # Armor
        elif row['Q_Index'] > 0.98: q_lbl = "[PURE]"  # Tungsten
        elif row['Q_Index'] < 0.80: q_lbl = "[LEAKY]" # Calcium
        
        # Audit Verdict
        verdict = "OK"
        if row['Audit_Diff'] > 0.5: verdict = "MISMATCH" # > 0.5 eV error
        
        star = "★" if row['Audit_Diff'] < 0.2 else ""

        print(f"{row['El']:<3} {row['Q_Index']:<6.2f} | {row['E_Ideal']:<5.2f} {row['WF']:<5.2f} | {row['Deficit_Real']:<10.2f} {row['Deficit_Pred']:<10.2f} | {verdict} {star} {q_lbl}")

    print("-" * 100)
    print("LEGEND:")
    print(" LOST(Real): Amount of eV actually missing from ideal geometry.")
    print(" LOST(Pred): Amount of eV our Entropy Model predicts should be missing.")
    print(" MATCH: Means our specific entropy mechanism explains the energy loss accurately.")

simureality_v12_system_auditor()
