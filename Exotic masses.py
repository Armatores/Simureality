import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="PDG SQLite Explorer", layout="wide")
st.title("🗄️ База Данных PDG (SQLite)")

DB_FILE = "pdg-2026.db" # Убедись, что файл называется так!

if not os.path.exists(DB_FILE):
    st.error(f"❌ База данных '{DB_FILE}' не найдена. Положите файл рядом со скриптом.")
else:
    st.success("✅ База данных SQLite успешно подключена!")
    
    # 1. Подключаемся к базе данных
    conn = sqlite3.connect(DB_FILE)
    
    # 2. Узнаем, какие вообще таблицы есть внутри файла ЦЕРНа
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql_query(tables_query, conn)
    
    st.markdown("### 1. Внутренняя структура базы (Таблицы)")
    st.dataframe(tables_df)
    
    # 3. Скорее всего, главная таблица называется 'particles' или 'pdg_data'
    # Давай вытащим список колонок и первые 50 строк из самой большой таблицы
    # (Обычно это первая или вторая таблица в списке)
    if not tables_df.empty:
        # Берем имя таблицы, которая похожа на частицы
        target_table = "particles" if "particles" in tables_df['name'].values else tables_df.iloc[0]['name']
        
        st.markdown(f"### 2. Содержимое таблицы: `{target_table}`")
        
        # SQL-запрос: вытащить всё из таблицы
        data_query = f"SELECT * FROM {target_table} LIMIT 1000;"
        try:
            df_particles = pd.read_sql_query(data_query, conn)
            st.dataframe(df_particles, use_container_width=True)
            
            st.markdown("### 🔍 Поиск экзотики SQL-запросом")
            st.write("Скрипт ищет наши частицы напрямую через SQL...")
            
            # Если в таблице есть колонка 'name' или 'description'
            search_cols = [col for col in df_particles.columns if 'name' in col.lower() or 'desc' in col.lower()]
            if search_cols:
                col_name = search_cols[0]
                # Ищем X(3872) и Z_c(4430) прямо в базе
                exotic_query = f"""
                SELECT * FROM {target_table} 
                WHERE {col_name} LIKE '%3872%' 
                   OR {col_name} LIKE '%4430%'
                   OR {col_name} LIKE '%6900%'
                """
                df_exotic = pd.read_sql_query(exotic_query, conn)
                if not df_exotic.empty:
                    st.success("🎯 Экзотические частицы найдены в базе!")
                    st.dataframe(df_exotic)
                else:
                    st.warning("Частицы по этим цифрам не найдены.")
                    
        except Exception as e:
            st.error(f"Ошибка чтения таблицы: {e}")
            
    conn.close()
