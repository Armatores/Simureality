import math
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

# =====================================================================
# SIMUREALITY: DYNAMIC STATE MACHINE (V24 CORE)
# =====================================================================

GAMMA_SYS = 1.0418               
VACUUM_GATE = 3.325              
BUFFER_RADIUS = VACUUM_GATE / 2  
STATIC_BASE_LOCK = 286.5         
VOLUME_BONUS = 12.75             

def calculate_asymmetric_overlap(d, r1, r2):
    if d >= r1 + r2 or d <= 0: return 0.0
    if d <= abs(r1 - r2): return (4/3) * math.pi * (min(r1, r2)**3)
    d1 = (d**2 - r2**2 + r1**2) / (2 * d)
    d2 = d - d1
    h1 = r1 - d1
    h2 = r2 - d2
    return ((math.pi * h1**2 / 3) * (3 * r1 - h1)) + ((math.pi * h2**2 / 3) * (3 * r2 - h2))

def parse_node_topology(mol_h, atom, exclude_idx):
    t_pen, r_cash = 0.0, 0.0
    atomic_num, hyb = atom.GetAtomicNum(), atom.GetHybridization()
    if atomic_num == 1: return 0.0, 0.0

    if atomic_num == 6:
        if hyb == Chem.rdchem.HybridizationType.SP: t_pen += 140.0
        elif hyb == Chem.rdchem.HybridizationType.SP2:
            has_O_sink = any(mol_h.GetBondBetweenAtoms(atom.GetIdx(), n.GetIdx()).GetBondTypeAsDouble() == 2.0 and n.GetAtomicNum() == 8 for n in atom.GetNeighbors() if n.GetIdx() != exclude_idx)
            if has_O_sink: r_cash += 40.0 
            else: t_pen += 45.0  

    elif atomic_num in [7, 8]:
        if hyb in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]: r_cash += 50.0  
        
    return t_pen, r_cash

def parse_edge_topology(mol_h, a1, a2, bo):
    e_pen, e_cash = 0.0, 0.0
    hyb1, hyb2 = a1.GetHybridization(), a2.GetHybridization()
    if bo == 1.0 and (hyb1 in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]) and (hyb2 in [Chem.rdchem.HybridizationType.SP2, Chem.rdchem.HybridizationType.SP]):
        e_cash -= 40.0 
    return e_pen, e_cash

def evaluate_transaction(smiles, target_bond_indices):
    """Оценивает энергию конкретной транзакции (связи) в заданном состоянии графа"""
    mol = Chem.MolFromSmiles(smiles)
    mol_h = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol_h, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol_h)
    conf = mol_h.GetConformer()
    pt = Chem.GetPeriodicTable()

    idx1, idx2 = target_bond_indices
    a1, a2 = mol_h.GetAtomWithIdx(idx1), mol_h.GetAtomWithIdx(idx2)
    bond = mol_h.GetBondBetweenAtoms(idx1, idx2)
    bo = bond.GetBondTypeAsDouble()

    pos1, pos2 = np.array(conf.GetAtomPosition(idx1)), np.array(conf.GetAtomPosition(idx2))
    d_actual = np.linalg.norm(pos1 - pos2)
    
    r_cov1, r_cov2 = pt.GetRcovalent(a1.GetAtomicNum()), pt.GetRcovalent(a2.GetAtomicNum())
    v_total_buf = calculate_asymmetric_overlap(d_actual, BUFFER_RADIUS, BUFFER_RADIUS)
    v_net = max(0.0, v_total_buf - calculate_asymmetric_overlap(d_actual, r_cov1, BUFFER_RADIUS) - calculate_asymmetric_overlap(d_actual, r_cov2, BUFFER_RADIUS))

    tp1, rc1 = parse_node_topology(mol_h, a1, idx2)
    tp2, rc2 = parse_node_topology(mol_h, a2, idx1)
    ep, ec = parse_edge_topology(mol_h, a1, a2, bo)

    hw_profit = ((bo * STATIC_BASE_LOCK) + (VOLUME_BONUS * v_net)) * GAMMA_SYS
    tension_penalty = tp1 + tp2 + ep
    resonance_cashback = max(0.0, rc1 + rc2 + ec)
    
    transaction_energy = hw_profit + tension_penalty - resonance_cashback
    
    return {
        "bo": bo, "v_net": v_net, "hw": hw_profit, "tax": tension_penalty, 
        "cash": resonance_cashback, "total": transaction_energy
    }

print("\n🌐 СИМУЛЯЦИЯ ПОЭТАПНОЙ СБОРКИ: УГЛЕКИСЛЫЙ ГАЗ (CO2)\n")

# ШАГ 1: Углерод + Кислород = Угарный газ
print("ШАГ 1: Формирование ядра (C + O -> CO)")
print("  Матрица максимизирует порты, формируя тройную связь.")
step1 = evaluate_transaction("[C-]#[O+]", (0, 1)) # Индексы C и O
print(f"  -> BO: {step1['bo']}, V_net: {step1['v_net']:.2f} Å³")
print(f"  -> HW Профит: {step1['hw']:.1f} кДж, Налог Сжатия: {step1['tax']:.1f} кДж")
print(f"  => Энергия Транзакции 1: {step1['total']:.1f} kJ/mol\n")

# ШАГ 2: Угарный газ + Кислород = Углекислый газ
print("ШАГ 2: Реструктуризация (CO + O -> CO2)")
print("  Матрица распаковывает тройную связь для приема второго кислорода.")
step2 = evaluate_transaction("O=C=O", (0, 1)) # Берем одну из связей C=O
print(f"  -> BO: {step2['bo']}, V_net: {step2['v_net']:.2f} Å³")
print(f"  -> HW Профит: {step2['hw']:.1f} кДж, Налог Сжатия: {step2['tax']:.1f} кДж")
print(f"  => Энергия Транзакции 2: {step2['total']:.1f} kJ/mol\n")

# ИТОГ
total_atomization = step1['total'] + step2['total']
print(f"=== ПОЛНАЯ ЭНЕРГИЯ АТОМИЗАЦИИ (ΣK): {total_atomization:.1f} kJ/mol ===")
print("  (Экспериментальное значение CO2: ~1608 kJ/mol)\n")
