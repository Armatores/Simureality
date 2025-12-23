import pandas as pd
import numpy as np

def simureality_v11_entropy_metabolism():
    print(f"{'='*100}")
    print(f" SIMUREALITY V11: ENTROPY METABOLISM MODEL")
    print(f" CONCEPT: Work Function = Total Geometric Energy - Entropy Losses")
    print(f"{'='*100}")

    # --- CONSTANTS ---
    # Геометрические идеалы (Максимальный Порядок)
    PHI = (1 + np.sqrt(5)) / 2
    GEO_FCC = 1 / PHI             # 0.618
    GEO_BCC = 1 / np.sqrt(3)      # 0.577
    
    # ENTROPY PARAMETERS
    # Порог, ниже которого система начинает "течь" (генерировать энтропию)
    STABILITY_THRESHOLD = 200 # MPa (Yield Strength)
    
    # Порог плотности: если объем > 12, энтропия вакуума "размывает" заряд
    VACUUM_NOISE_THRESHOLD = 12.0 
    
    # Идеал Гексагона
    IDEAL_HCP_CA = 1.633

    # --- DATASET ---
    # Мы смотрим на материал как на систему с параметрами прочности и плотности
    data = [
        # === HIGH STABILITY SYSTEMS (Hard & Dense) ===
        {'El': 'W',  'St':'BCC', 'Ion':7.86, 'WF':4.55, 'Yield':750, 'Vol':9.53, 'CA':0,    'Group':'STABLE'},
        {'El': 'Fe', 'St':'BCC', 'Ion':7.90, 'WF':4.50, 'Yield':250, 'Vol':7.09, 'CA':0,    'Group':'STABLE'},
        {'El': 'Ta', 'St':'BCC', 'Ion':7.55, 'WF':4.25, 'Yield':180, 'Vol':10.8, 'CA':0,    'Group':'STABLE'},
        
        # === DISSIPATIVE SYSTEMS (Soft -> High Internal Entropy) ===
        # Золото "платит" за свою мягкость
        {'El': 'Au', 'St':'FCC', 'Ion':9.22, 'WF':5.10, 'Yield':20,  'Vol':10.2, 'CA':0,    'Group':'DISSIPATIVE'},
        {'El': 'Ag', 'St':'FCC', 'Ion':7.58, 'WF':4.26, 'Yield':15,  'Vol':10.2, 'CA':0,    'Group':'DISSIPATIVE'},
        {'El': 'Cu', 'St':'FCC', 'Ion':7.73, 'WF':4.65, 'Yield':70,  'Vol':7.11, 'CA':0,    'Group':'DISSIPATIVE'},

        # === DECOHERENT SYSTEMS (Fluffy -> Vacuum Noise) ===
        # Кальций и Магний теряют энергию из-за низкой плотности
        {'El': 'Mg', 'St':'HCP', 'Ion':7.65, 'WF':3.66, 'Yield':90,  'Vol':14.0, 'CA':1.62, 'Group':'DECOHERENT'},
        {'El': 'Ca', 'St':'FCC', 'Ion':6.11, 'WF':2.87, 'Yield':12,  'Vol':26.2, 'CA':0,    'Group':'DECOHERENT'},
        {'El': 'Sr', 'St':'FCC', 'Ion':5.69, 'WF':2.59, 'Yield':8,   'Vol':33.9, 'CA':0,    'Group':'DECOHERENT'},
        
        # === NOISY SYSTEMS (Distorted Geometry) ===
        # Цинк теряет энергию на геометрическом шуме
        {'El': 'Zn', 'St':'HCP', 'Ion':9.39, 'WF':4.33, 'Yield':100, 'Vol':9.16, 'CA':1.856,'Group':'NOISY'},
        {'El': 'Cd', 'St':'HCP', 'Ion':8.99, 'WF':4.22, 'Yield':30,  'Vol':13.0, 'CA':1.886,'Group':'NOISY'},

        # === ARMORED SYSTEMS (Negentropic) ===
        # Алюминий использует оксид как "Щит от Энтропии" (снижает потери)
        {'El': 'Al', 'St':'FCC', 'Ion':5.99, 'WF':4.28, 'Yield':30,  'Vol':10.0, 'CA':0,    'Group':'ARMORED'},
        {'El': 'Ga', 'St':'Orth','Ion':6.00, 'WF':4.20, 'Yield':10,  'Vol':11.8, 'CA':0,    'Group':'ARMORED'},
    ]
    df = pd.DataFrame(data)

    # --- CALCULATION ENGINE ---

    # 1. TOTAL GEOMETRIC ENERGY (E_total)
    # Максимально возможный порядок
    df['Geo_Coeff'] = np.where(df['St'] == 'BCC', GEO_BCC, GEO_FCC)
    df['E_Total'] = df['Ion'] * df['Geo_Coeff']

    # 2. ENTROPY LOSS: DISSIPATION (Пластичность)
    # Если прочность ниже порога, система тратит энергию на поддержание формы.
    # Loss ~ 1/Yield
    # Для ARMORED потери блокируются (оксид держит форму на поверхности)
    df['Loss_Dissipation'] = np.where(
        (df['Yield'] < STABILITY_THRESHOLD) & (df['Group'] != 'ARMORED'),
        (2.4 / df['Yield']).clip(upper=0.35), # Макс потеря 35%
        0.0
    )

    # 3. ENTROPY LOSS: DECOHERENCE (Рыхлость)
    # Если объем > 12, вакуум "съедает" сигнал.
    # Loss ~ (Vol - 12)
    df['Loss_Decoherence'] = np.where(
        df['Vol'] > VACUUM_NOISE_THRESHOLD,
        1 - ((VACUUM_NOISE_THRESHOLD / df['Vol']) ** 0.35),
        0.0
    )

    # 4. ENTROPY LOSS: NOISE (Искажение решетки)
    # Если c/a отличается от 1.633, возникает шум.
    # Loss ~ Distortion^2
    df['Distort_Ratio'] = np.where(df['CA'] > 0, df['CA'] / IDEAL_HCP_CA, 1.0)
    df['Loss_Noise'] = np.where(
        df['Distort_Ratio'] > 1.05,
        1 - (1 / (df['Distort_Ratio']**2)),
        0.0
    )
    
    # 5. NEGENTROPY BOOST (Броня)
    # Оксид добавляет порядок
    df['Boost_Armor'] = np.where(
        df['Group'] == 'ARMORED',
        (1.0418 ** 3) - 1, # Добавка от валентности 3
        0.0
    )

    # --- FINAL STATE ---
    # WF = E_Total * (1 - Losses + Boost)
    # Суммируем все потери энтропии
    df['Total_Entropy'] = df['Loss_Dissipation'] + df['Loss_Decoherence'] + df['Loss_Noise']
    
    # Применяем к энергии
    df['WF_Pred'] = df['E_Total'] * (1 - df['Total_Entropy'] + df['Boost_Armor'])
    
    df['Error'] = abs(df['WF_Pred'] - df['WF']) / df['WF'] * 100

    # --- OUTPUT ---
    print(f"{'El':<3} {'Group':<12} | {'E_Tot':<5} {'Entropy':<7} {'Real':<5} | {'Error':<6} | {'Physics'}")
    print("-" * 100)
    
    for i, row in df.iterrows():
        # Physics explanation string
        reasons = []
        if row['Loss_Dissipation'] > 0: reasons.append(f"Dissip -{row['Loss_Dissipation']*100:.0f}%")
        if row['Loss_Decoherence'] > 0: reasons.append(f"Decoh -{row['Loss_Decoherence']*100:.0f}%")
        if row['Loss_Noise'] > 0: reasons.append(f"Noise -{row['Loss_Noise']*100:.0f}%")
        if row['Boost_Armor'] > 0: reasons.append(f"Armor +{row['Boost_Armor']*100:.0f}%")
        if not reasons: reasons.append("Stable State")
        
        physics = ", ".join(reasons)
        
        star = "★" if row['Error'] < 3.0 else ""
        print(f"{row['El']:<3} {row['Group']:<12} | {row['E_Total']:<5.2f} {row['WF_Pred']:<7.2f} {row['WF']:<5.2f} | {row['Error']:<6.1f} | {physics} {star}")

simureality_v11_entropy_metabolism()
