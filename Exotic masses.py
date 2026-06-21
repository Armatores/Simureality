import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="PDG Particles Explorer", layout="wide")
st.title("🗄️ Охота на Экзотику (Таблица Particles)")

DB_FILE = "pdg-2026.db"

if not os.path.exists(DB_FILE):
    st.error(f"❌ Файл {DB_FILE} не найден.")
else:
    conn = sqlite3.connect(DB_FILE)
    
    # Жестко выбираем нужную нам таблицу!
    target_table = "particles"
    
    st.markdown(f"### 🔍 Прямой SQL-запрос к таблице `{target_table}`")
    
    try:
        # Ищем наши частицы напрямую по колонке 'name' (в SQLite она обычно так и называется)
        search_query = f"""
        SELECT * FROM {target_table} 
        WHERE name LIKE '%3872%' 
           OR name LIKE '%3900%'
           OR name LIKE '%4430%'
           OR name LIKE '%4312%'
           OR name LIKE '%4440%'
           OR name LIKE '%6900%'
           OR name LIKE '%2317%'
        """
        df_exotic = pd.read_sql_query(search_query, conn)
        
        if not df_exotic.empty:
            st.success("🎯 БИНГО! Вот наши экзотические частицы прямо из ЦЕРНа:")
            st.dataframe(df_exotic, use_container_width=True)
            
            # Предлагаем код для словаря EXOTIC_MAP на основе того, что нашли
            st.markdown("### 🛠 Что делать дальше?")
            st.write("Скопируй точные имена из колонки **name** (или **description**) в наш словарь `EXOTIC_MAP` для финального калькулятора.")
        else:
            st.warning("В колонке 'name' таких цифр нет. Возможно, колонка называется иначе. Вывожу 500 частиц, чтобы посмотреть структуру базы глазами:")
            fallback_query = f"SELECT * FROM {target_table} LIMIT 500;"
            df_fallback = pd.read_sql_query(fallback_query, conn)
            st.dataframe(df_fallback, use_container_width=True)
            
    except Exception as e:
        st.error(f"Ошибка БД: {e}")
        
    conn.close()
