import streamlit as st
import pandas as pd

# =====================================================================
# SIMUREALITY: V-PROBE (DATASET X-RAY)
# =====================================================================

st.set_page_config(page_title="V-Probe: Dataset X-Ray", layout="centered")
st.title("🛠 V-Probe: Data Structure X-Ray")
st.markdown("Сканирование заголовков и первых 5 строк архива `bde-db2.csv.gz` для выявления синтаксиса Матрицы.")

file_path = "bde-db2.csv.gz"

try:
    # Читаем только 5 строк для мгновенного ответа
    df = pd.read_csv(file_path, compression='gzip', nrows=5)
    
    st.success("✅ Архив успешно вскрыт. Чтение заголовков завершено.")
    
    st.subheader("1. Структура Колонок (Raw Headers)")
    st.write(df.columns.tolist())
    
    st.subheader("2. Дамп Памяти (Первые 5 транзакций)")
    st.dataframe(df)
    
    st.info("Внимательно изучи колонку с типами связей. Ищем, как датасет кодирует C-C, C=C, O-H и т.д. Скопируй эти данные для написания патча.")
    
except Exception as e:
    st.error(f"❌ Ошибка аппаратного чтения: {e}")
    st.markdown("Проверь, лежит ли файл `bde-db2.csv.gz` в корневой папке скрипта.")
