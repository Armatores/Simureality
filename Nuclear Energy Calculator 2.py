import streamlit as st
import pandas as pd
import math
import io

# ==========================================================================================
# SIMUREALITY: NUCLEAR CAD V6.0 (STREAMLIT EDITION)
# ==========================================================================================

st.set_page_config(page_title="Simureality Nuclear CAD", layout="wide")

class GridPhysicsEngine:
    def __init__(self):
        self.m_e = 0.511  
        self.PI = math.pi
        self.gamma_1D = 2.0 / math.sqrt(3.0)        
        self.gamma_vol = self.gamma_1D ** (1.0/3.0) 
        self.gamma_sys = 1.0418                     
        self.eta_fcc = self.PI / (3 * math.sqrt(2)) 
        self.E_link = 4 * self.m_e * self.gamma_1D  
        self.E_alpha = 12 * self.E_link             
        self.a_V = 6 * self.E_link * self.gamma_sys 
        self.a_S = 14.5                             
        self.a_C = self.eta_fcc / self.gamma_vol    
        self.a_Sym = 6 * self.E_link                
        self.delta = 12.0                           

    def geometric_shell_penalty(self, Z, N):
        shells = [2, 8, 20, 28, 50, 82, 126, 184]
        dist_Z = min([abs(Z - m) for m in shells])
        dist_N = min([abs(N - m) for m in shells])
        K_DEFORM = (4 * (1/137.036)) / (self.PI**2 * self.gamma_sys)
        if Z < 40: return 0
        return K_DEFORM * (dist_Z * dist_N) * (dist_Z + dist_N)**0.8

    def calculate_energy(self, Z, A):
        N = A - Z
        if Z <= 20:
            n_alpha = A // 4
            rem = A % 4
            links = 0 if n_alpha < 2 else 3 * n_alpha - 6
            E_geom = (n_alpha * self.E_alpha) + (links * self.E_link)
            if rem == 2: E_geom += self.E_link
            if rem == 3: 
                E_geom += 3.5 * self.E_link
                if Z == 2: E_geom -= self.a_C
            if N != Z and A >= 4: 
                 E_geom -= (self.E_alpha * math.sqrt(2/3)) * ((N-Z)**2) / A 
            return E_geom
        else:
            E_vol = self.a_V * A
            E_surf = self.a_S * (A**(2.0/3.0))
            E_coul = self.a_C * (Z*(Z-1)) / (A**(1.0/3.0))
            E_sym = self.a_Sym * ((N-Z)**2) / A
            if Z % 2 == 0 and N % 2 == 0: E_pair = self.delta / (A**(0.5))
            elif Z % 2 != 0 and N % 2 != 0: E_pair = -self.delta / (A**(0.5))
            else: E_pair = 0
            E_macro = E_vol - E_surf - E_coul - E_sym + E_pair
            return E_macro - self.geometric_shell_penalty(Z, N)

def parse_ame2020(file_bytes):
    dataset = []
    # Декодируем байты в текст
    content = file_bytes.getvalue().decode("utf-8")
    
    for line in content.split('\n'):
        if len(line) < 67 or line.startswith('1N-Z') or 'MASS EXCESS' in line or 'A T O M I C' in line:
            continue
        try:
            N = int(line[4:9])
            Z = int(line[9:14])
            A = int(line[14:19])
            el = line[20:23].strip()
            
            be_str = line[54:67].replace('#', '').strip()
            if not be_str or be_str == '*': continue
            
            be_per_n_kev = float(be_str)
            real_be_mev = (A * be_per_n_kev) / 1000.0
            
            if real_be_mev > 0:
                dataset.append((f"{A}{el}", Z, A, real_be_mev))
        except ValueError:
            continue
    return dataset

# Интерфейс Streamlit
st.title("Simureality: Grid Physics Binding Engine ⚛️")
st.markdown("""
**Движок валидации ГЦК-матрицы.** Загрузи сырой текстовый дамп `mass.mas20` из базы AME2020 для аппаратного бенчмарка.
""")

uploaded_file = st.file_uploader("Загрузить файл mass.mas20", type=["txt", "mas20", ""])

if uploaded_file is not None:
    st.info("Файл загружен. Запускаю компиляцию геометрии вакуума...")
    
    engine = GridPhysicsEngine()
    dataset = parse_ame2020(uploaded_file)
    
    if not dataset:
        st.error("Не удалось распарсить данные. Проверь формат файла.")
    else:
        results = []
        total_acc = 0
        
        # Индикатор прогресса
        progress_bar = st.progress(0)
        total_items = len(dataset)
        
        for i, (name, Z, A, real_be) in enumerate(dataset):
            sim_val = engine.calculate_energy(Z, A)
            acc = 100 * (1 - abs(sim_val - real_be)/real_be)
            if acc < 0: acc = 0
            total_acc += acc
            
            results.append({
                "Isotope": name,
                "Z": Z,
                "A": A,
                "AME2020 Exp (MeV)": round(real_be, 4),
                "Simureality (MeV)": round(sim_val, 4),
                "Accuracy (%)": round(acc, 2)
            })
            
            # Обновляем прогресс каждые 100 шагов для оптимизации UI
            if i % 100 == 0:
                progress_bar.progress(i / total_items)
                
        progress_bar.progress(1.0)
        
        df = pd.DataFrame(results)
        avg_acc = total_acc / total_items
        
        # Вывод статистики
        st.success(f"Рендер завершен! Проанализировано изотопов: **{total_items}**")
        st.metric(label="Средняя точность ГЦК-модели", value=f"{avg_acc:.3f}%")
        
        # Показ таблицы
        st.dataframe(df, use_container_width=True)
        
        # Кнопка для скачивания CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Скачать результаты (CSV)",
            data=csv,
            file_name='simureality_ame2020_benchmark.csv',
            mime='text/csv',
        )
