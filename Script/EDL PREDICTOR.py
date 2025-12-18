import math

def log_header(text):
    print(f"\n{'='*100}")
    print(f" {text}")
    print(f"{'='*100}")

# ==============================================================================
# SIMUREALITY: ELECTRO-GEOMETRIC DOUBLE LAYER (EDL) PREDICTOR
# Logic: Ions dock onto the FCC Lattice of the Electrode surface.
# ==============================================================================

def get_constants():
    # Наш "Золотой Набор"
    PI = math.pi
    ALPHA = 1 / 137.035999
    
    # Геометрия ГКЦ (FCC)
    # Максимальная плотность упаковки шаров (Kepler Conjecture)
    FCC_PACKING_LIMIT = PI / (3 * math.sqrt(2)) # ~0.74048
    
    # Налог на Систему (сопротивление среды/воды упорядочиванию)
    GAMMA_SYS = 1.0418 
    
    return FCC_PACKING_LIMIT, GAMMA_SYS, ALPHA

class IonLayerSimulation:
    def __init__(self, voltage_potential, concentration):
        # Исправлено: распаковка констант в правильные атрибуты класса
        self.pack_limit, self.gamma_sys, self.alpha = get_constants()
        
        self.voltage = voltage_potential # "Сила притяжения" (0.0 - 1.0)
        self.bulk_conc = concentration   # Концентрация в глубине (0.0 - 1.0)
        self.layers = []

    def run_docking(self, num_layers=10):
        """
        Симуляция послойного заполнения (Simureality Tetris).
        """
        remaining_field = self.voltage
        
        for i in range(num_layers):
            # 1. Желание ионов (Desire)
            distance_penalty = self.gamma_sys ** (i) 
            desire = (remaining_field / distance_penalty)
            
            # 2. Геометрический лимит (Capacity)
            # ИСПРАВЛЕНО: используем self.pack_limit
            capacity = self.pack_limit
            
            # 3. Реальная плотность
            docked_density = min(desire, capacity)
            
            # Не падаем ниже фона
            docked_density = max(docked_density, self.bulk_conc)
            
            # 4. Экранирование поля
            screening = docked_density * (1 - self.alpha)
            remaining_field -= screening
            if remaining_field < 0: remaining_field = 0
            
            self.layers.append({
                "layer_id": i+1,
                "density": docked_density,
                "field_after": remaining_field,
                # ИСПРАВЛЕНО: используем self.pack_limit для проверки насыщения
                "is_saturated": docked_density >= (self.pack_limit - 0.01)
            })

    def print_results(self):
        log_header(f"SIMUREALITY EDL: SURFACE POTENTIAL {self.voltage:.2f}")
        print(f"FCC Packing Limit (Hard Geometry): {self.pack_limit:.5f} (74%)")
        print(f"System Tax (Water Structure):      {self.gamma_sys:.4f}")
        print("-" * 80)
        print(f"{'LAYER':<6} | {'DENSITY (0-1)':<15} | {'GRAPHIC':<20} | {'STATUS'}")
        print("-" * 80)
        
        for L in self.layers:
            # Визуализация
            bar_len = int(L['density'] * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            
            status = "SATURATED (CRYSTAL)" if L['is_saturated'] else "DIFFUSE (LIQUID)"
            
            print(f" {L['layer_id']:<5} | {L['density']:.4f}          | {bar} | {status}")
            
        print("-" * 80)
        print("INTERPRETATION:")
        print("Layer density is physically capped at the FCC geometric limit (~0.74).")
        print("This creates the 'Solid' Helmholtz layer without complex differential equations.")

if __name__ == "__main__":
    # Сценарий 1: Низкий потенциал
    sim_low = IonLayerSimulation(voltage_potential=0.3, concentration=0.05)
    sim_low.run_docking()
    sim_low.print_results()
    
    # Сценарий 2: Высокий потенциал (Насыщение / Кристаллизация)
    sim_high = IonLayerSimulation(voltage_potential=2.5, concentration=0.05)
    sim_high.run_docking()
    sim_high.print_results()
