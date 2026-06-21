import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="PDG Database Explorer", layout="wide")
st.title("🗄️ Исследователь Базы PDG (SQLite)")

DB_FILE = "pdg-2026.db"

if not os.path.exists(DB_FILE):
    st.error(f"❌ Файл {DB_FILE} не найден.")
else:
    conn = sqlite3.connect(DB_FILE)
    
    # 1. Получаем список всех таблиц
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql_query(tables_query, conn)
    
    if not tables_df.empty:
        table_names = tables_df['name'].tolist()
        
        # 2. Делаем выпадающий список, чтобы ты мог сам выбрать таблицу!
        selected_table = st.selectbox("📂 Выберите таблицу для просмотра:", table_names)
        
        st.markdown(f"### Структура и данные таблицы: `{selected_table}`")
        
        try:
            # Читаем первые 1000 строк из выбранной таблицы
            df = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 1000;", conn)
            
            # Показываем список колонок (чтобы мы знали, где искать массу и имя)
            st.write("**Колонки в этой таблице:**", df.columns.tolist())
            
            # Показываем сами данные
            st.dataframe(df, use_container_width=True)
            
            # 3. Умный поиск по всей таблице
            st.markdown("---")
            st.markdown("### 🔍 Поиск по таблице")
            search_term = st.text_input("Введите значение для поиска (например, 3872 или X):")
            
            if search_term:
                # Ищем во всех текстовых колонках
                text_cols = df.select_dtypes(include=['object']).columns
                if not text_cols.empty:
                    # Строим запрос для поиска по всем текстовым колонкам
                    conditions = " OR ".join([f"{col} LIKE '%{search_term}%'" for col in text_cols])
                    search_query = f"SELECT * FROM {selected_table} WHERE {conditions}"
                    
                    search_results = pd.read_sql_query(search_query, conn)
                    if not search_results.empty:
                        st.success(f"Найдено {len(search_results)} совпадений!")
                        st.dataframe(search_results, use_container_width=True)
                    else:
                        st.warning("Ничего не найдено.")
                else:
                    st.info("В этой таблице нет текстовых колонок для поиска.")
                    
        except Exception as e:
            st.error(f"Ошибка при чтении таблицы {selected_table}: {e}")
            
    else:
        st.warning("База данных пуста (нет таблиц).")
        
    conn.close()
