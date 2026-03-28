def run_beta_cascade(Z_start, N_start):
    chain = []
    current_Z, current_N = Z_start, N_start
    C_TAX = E_LINK * np.sqrt(2) # Наш новый мощный диагональный импеданс
    
    def get_beta_profit(Z, N):
        if Z <= 0 or N <= 0: return -float('inf')
        base_profit = calculate_topological_profit(Z, N)
        A = Z + N
        routing_complexity = (Z * (Z - 1)) / 2.0 
        discrete_diameter = get_discrete_graph_diameter(A)
        coulomb_penalty = C_TAX * (routing_complexity / discrete_diameter)
        return base_profit - coulomb_penalty

    while True:
        profit_current = get_beta_profit(current_Z, current_N)
        
        # 1-шаговое сканирование
        profit_b_minus_1 = get_beta_profit(current_Z + 1, current_N - 1)
        profit_b_plus_1 = get_beta_profit(current_Z - 1, current_N + 1)
        
        # 2-шаговое сканирование (Двойной бета-распад / Туннелирование)
        profit_b_minus_2 = get_beta_profit(current_Z + 2, current_N - 2)
        profit_b_plus_2 = get_beta_profit(current_Z - 2, current_N + 2)
        
        best_profit = profit_current
        next_step = None
        decay_type = "Stable (Optimal)"
        step_gain = 0.0
        
        # Сначала проверяем классический 1-шаговый спуск
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
            
        # Если 1-шагового спуска нет, проверяем ТУННЕЛИРОВАНИЕ
        if next_step is None:
            if profit_b_minus_2 > profit_current:
                # Фиксируем транзитный (виртуальный) шаг
                chain.append({
                    "Protons (Z)": current_Z + 1,
                    "Neutrons (N)": current_N - 1,
                    "Mass (A)": current_Z + current_N,
                    "Decay Triggered": "Virtual State (Transit)",
                    "Topological Profit (MeV)": profit_b_minus_1,
                    "Step Gain (ΔQ)": profit_b_minus_1 - profit_current
                })
                # Жестко коммитим приземление на 2-й шаг
                next_step = (current_Z + 2, current_N - 2)
                decay_type = "Double β- Decay"
                step_gain = profit_b_minus_2 - profit_b_minus_1
                profit_current = profit_b_minus_1 # для корректного отображения профита
                
            elif profit_b_plus_2 > profit_current:
                # Фиксируем транзитный (виртуальный) шаг
                chain.append({
                    "Protons (Z)": current_Z - 1,
                    "Neutrons (N)": current_N + 1,
                    "Mass (A)": current_Z + current_N,
                    "Decay Triggered": "Virtual State (Transit)",
                    "Topological Profit (MeV)": profit_b_plus_1,
                    "Step Gain (ΔQ)": profit_b_plus_1 - profit_current
                })
                # Жестко коммитим приземление на 2-й шаг
                next_step = (current_Z - 2, current_N + 2)
                decay_type = "Double β+ / EC"
                step_gain = profit_b_plus_2 - profit_b_plus_1
                profit_current = profit_b_plus_1 # для корректного отображения профита

        # Добавляем финальный/текущий шаг в лог
        chain.append({
            "Protons (Z)": next_step[0] if next_step else current_Z,
            "Neutrons (N)": next_step[1] if next_step else current_N,
            "Mass (A)": (next_step[0]+next_step[1]) if next_step else (current_Z+current_N),
            "Decay Triggered": decay_type,
            "Topological Profit (MeV)": best_profit if next_step else profit_current,
            "Step Gain (ΔQ)": step_gain
        })
        
        if not next_step or len(chain) > 20: # увеличил лимит на всякий случай
            break
            
        current_Z, current_N = next_step
        
    return pd.DataFrame(chain)
