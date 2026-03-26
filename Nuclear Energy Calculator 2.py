import os

# Интерфейс Streamlit
st.title("Simureality: Grid Physics Binding Engine ⚛️")
st.markdown("**Движок валидации ГЦК-матрицы.** Аппаратный бенчмарк по сырым данным AME2020.")

# 1. АВТОМАТИЧЕСКИЙ ЗАХВАТ ФАЙЛА ИЗ РЕПОЗИТОРИЯ
file_path_txt = "mass.txt"
file_path_mas = "mass.mas20"

dataset = None
engine = GridPhysicsEngine()

# Ищем файл локально в корне
if os.path.exists(file_path_txt):
    with open(file_path_txt, "r", encoding="utf-8") as f:
        dataset = parse_ame2020(io.StringIO(f.read()))
    st.success(f"База данных {file_path_txt} автоматически загружена из ядра.")
elif os.path.exists(file_path_mas):
    with open(file_path_mas, "r", encoding="utf-8") as f:
        dataset = parse_ame2020(io.StringIO(f.read()))
    st.success(f"База данных {file_path_mas} автоматически загружена из ядра.")
else:
    st.warning("Локальный файл не найден. Используйте ручную загрузку.")
    # ИСПРАВЛЕННЫЙ UPLOADER (Без пустой строки)
    uploaded_file = st.file_uploader("Загрузить файл базы масс", type=["txt", "mas20", "csv"])
    if uploaded_file is not None:
        dataset = parse_ame2020(uploaded_file)

# 2. РЕНДЕР И ВЫЧИСЛЕНИЯ
if dataset:
    results = []
    total_acc = 0
    total_items = len(dataset)
    
    progress_bar = st.progress(0)
    
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
        
        if i % 100 == 0:
            progress_bar.progress(i / total_items)
            
    progress_bar.progress(1.0)
    
    df = pd.DataFrame(results)
    avg_acc = total_acc / total_items
    
    st.metric(label="Средняя точность ГЦК-модели", value=f"{avg_acc:.3f}%")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Скачать результаты (CSV)",
        data=csv,
        file_name='simureality_ame2020_benchmark.csv',
        mime='text/csv',
    )
elif not os.path.exists(file_path_txt) and not os.path.exists(file_path_mas):
    st.error("Жду входных данных для компиляции.")
