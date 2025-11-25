import numpy as np
import matplotlib.pyplot as plt

def run_simureality_experiment():
    print("--- ЗАПУСК СИМУЛЯЦИИ VECTOR REALISM (APPENDIX C) ---")
    
    # 1. КОНСТАНТЫ И НАСТРОЙКИ
    NUM_TRILEXES = 10000  # Количество частиц (трилексов)
    
    # Генерируем "неполяризованный свет": случайные углы от 0 до 360 градусов
    initial_phases = np.random.uniform(0, 2 * np.pi, NUM_TRILEXES)
    
    # Создаем массив векторов (Трилексов) с амплитудой 1
    # T = [cos(phi), sin(phi)]
    trilexes_x = np.cos(initial_phases)
    trilexes_y = np.sin(initial_phases)
    
    # Изначальная интенсивность (сумма квадратов амплитуд)
    initial_intensity = np.sum(trilexes_x**2 + trilexes_y**2)
    print(f"1. Источник сгенерировал {NUM_TRILEXES} трилексов.")
    print(f"   Начальная интенсивность: {initial_intensity:.2f}")

    # 2. ПЕРВЫЙ ФИЛЬТР (ПОЛЯРИЗАТОР A) - Вертикальный (90 градусов)
    angle_A = np.pi / 2 
    axis_A_x = np.cos(angle_A)
    axis_A_y = np.sin(angle_A)
    
    # ПРИМЕНЯЕМ ПРОЕКЦИЮ (Appendix C.2)
    # P = (T . A) * A
    dot_products_A = trilexes_x * axis_A_x + trilexes_y * axis_A_y
    
    # Векторы после фильтра А
    trilexes_after_A_x = dot_products_A * axis_A_x
    trilexes_after_A_y = dot_products_A * axis_A_y
    
    intensity_after_A = np.sum(trilexes_after_A_x**2 + trilexes_after_A_y**2)
    transmission_A = intensity_after_A / initial_intensity
    
    print(f"2. Проход через Поляризатор А.")
    print(f"   Прошло энергии: {transmission_A*100:.2f}% (Теория: 50%)")
    
    # 3. ВТОРОЙ ФИЛЬТР (АНАЛИЗАТОР B) - Вращаем и проверяем закон Малюса
    relative_angles_deg = np.linspace(0, 180, 50) 
    simulated_results = []
    theoretical_results = []
    
    print("3. Запуск вращения Анализатора B...")
    
    for rel_angle_deg in relative_angles_deg:
        # Угол фильтра B = Угол А + смещение
        angle_B = angle_A + np.radians(rel_angle_deg)
        
        axis_B_x = np.cos(angle_B)
        axis_B_y = np.sin(angle_B)
        
        # Проецируем векторы, прошедшие через А, на ось B
        dot_products_B = trilexes_after_A_x * axis_B_x + trilexes_after_A_y * axis_B_y
        
        trilexes_after_B_x = dot_products_B * axis_B_x
        trilexes_after_B_y = dot_products_B * axis_B_y
        
        intensity_final = np.sum(trilexes_after_B_x**2 + trilexes_after_B_y**2)
        
        # Нормируем (I / I_0)
        ratio = intensity_final / intensity_after_A
        simulated_results.append(ratio)
        
        # Теория: cos^2(theta)
        theoretical_results.append(np.cos(np.radians(rel_angle_deg))**2)

    # 4. ВИЗУАЛИЗАЦИЯ
    plt.figure(figsize=(10, 6))
    plt.plot(relative_angles_deg, theoretical_results, label='Theoretical Law (Malus): cos²(θ)', color='red', linewidth=2)
    plt.scatter(relative_angles_deg, simulated_results, label='Simureality Vector Projection', color='blue', alpha=0.7, s=30)
    
    plt.title('Verification of Appendix C: Malus\'s Law Derivation')
    plt.xlabel('Relative Angle (Degrees)')
    plt.ylabel('Intensity (I / I₀)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Сохраняем график в файл (если среда не поддерживает вывод окна)
    plt.savefig('simureality_plot.png')
    print("График сохранен как 'simureality_plot.png' и отображается на экране.")
    plt.show()

if __name__ == "__main__":
    run_simureality_experiment()
```
