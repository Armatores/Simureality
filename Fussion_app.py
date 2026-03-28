# Локальная константа электростатического напряжения
C_TAX = 0.58 

def run_beta_cascade(Z_start, N_start):
    chain = []
    current_Z, current_N = Z_start, N_start
    
    # Кастомная функция профита для микро-дефрагментации с учетом кулоновского импеданса
    def get_beta_profit(Z, N):
        base_profit = calculate_topological_profit(Z, N)
        coulomb_penalty = C_TAX * (Z**2) / ((Z+N)**(1/3))
        return base_profit - coulomb_penalty

    while True:
        profit_current = get_beta_profit(current_Z, current_N)
        
        # 1-шаговое сканирование
        profit_b_minus_1 = get_beta_profit(current_Z + 1, current_N - 1)
        profit_b_plus_1 = get_beta_profit(current_Z - 1, current_N + 1)
        
        # 2-шаговое сканирование (Квантовое туннелирование через ловушки четности)
        profit_b_minus_2 = get_beta_profit(current_Z + 2, current_N - 2)
        profit_b_plus_2 = get_beta_profit(current_Z - 2, current_N + 2)
        
        best_profit = profit_current
        next_step = None
        decay_type = "Stable (Optimal)"
        step_gain = 0.0
        
        # Проверяем чистый 1-шаговый градиент
        if profit_b_minus_1 > best_profit:
            best_profit = profit_b_minus_1
            next_step = (current_Z + 1, current_N - 1)
            decay_type = "β- Decay"
            step_gain = profit_b_minus_1 - profit_current
        elif profit_b_plus_1 > best_profit:
            best_profit = profit_b_plus_1
            next_step = (current_Z - 1, current_N + 1)
            decay_type = "β+ / EC"
            step_gain = profit_b_plus_1 - profit_current
            
        # Проверка ТУННЕЛИРОВАНИЯ (если 1-й шаг убыточный, но 2-й пробивает потолок)
        if next_step is None:
            if profit_b_minus_2 > profit_current:
                next_step = (current_Z + 1, current_N - 1)
                decay_type = "β- Decay (Tunneling)"
                step_gain = profit_b_minus_1 - profit_current
            elif profit_b_plus_2 > profit_current:
                next_step = (current_Z - 1, current_N + 1)
                decay_type = "β+ / EC (Tunneling)"
                step_gain = profit_b_plus_1 - profit_current

        chain.append({
            "Protons (Z)": current_Z,
            "Neutrons (N)": current_N,
            "Mass (A)": current_Z + current_N,
            "Decay Triggered": decay_type,
            "Topological Profit (MeV)": profit_current,
            "Step Gain (ΔQ)": step_gain
        })
        
        if not next_step or len(chain) > 15:
            break
            
        current_Z, current_N = next_step
        
    return pd.DataFrame(chain)
