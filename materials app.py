import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Simureality: Material Interface Calculator",
    page_icon="⚛️",
    layout="wide"
)
# --- DISCLAIMER / HOW TO READ ---
with st.expander("ℹ️ How to interpret the Simureality Score (Read First!)"):
    st.markdown("""
    **1. What this tool DOES calculate:**
    It calculates the **Geometric and Mechanical Potential** for an interface to exist at a specific Temperature ($T$).
    * **Geometric Resonance:** Do the atomic lattices fit together? (Volume Mismatch).
    * **Mechanical Wetting:** Can the material deform to fill voids? (Yield Strength).
    * **Entropic Stability:** Does thermal noise disrupt the lattice connection?

    **2. What this tool does NOT calculate:**
    It ignores **Chemical Reactivity** and **Time-dependent degradation**.
    * It does *not* predict intermetallic phase formation (e.g., Purple Plague in Au-Al).
    * It does *not* predict corrosion or oxidation over time.
    
    **3. The "Gallium Paradox" (High Score Warning):**
    A score of **100/100** means **Maximum Affinity**.
    * In stable systems (like Ni-Cu), this means a perfect solid solution.
    * In reactive systems (like Ga-Al), this means **aggressive wetting** which may lead to embrittlement.
    
    > **Rule of Thumb:** Use this tool to find materials that *physically fit*. Then check Phase Diagrams to ensure they are chemically safe.
    """)
# --- 1. LOAD DATABASE ---
@st.cache_data
def load_data():
    try:
        # Пытаемся загрузить из той же папки
        df = pd.read_csv('materials_db.csv')
        return df
    except FileNotFoundError:
        st.error("Файл 'materials_db.csv' не найден! Пожалуйста, создайте его в папке со скриптом.")
        return pd.DataFrame()

df = load_data()

# --- 2. PHYSICS ENGINE (The Master Equation v18) ---
def calculate_compatibility(substrate, candidate, temp_k, priority_mode):
    """
    Рассчитывает Simureality Score (0-100) или GOD MODE (999).
    """
    # A. SUPERCONDUCTIVITY CHECK (GOD MODE)
    # Если мы в режиме "Cryo" или "General", и температура ниже Tc кандидата
    if temp_k < candidate['Tc'] and candidate['Tc'] > 0:
        return 999.0, "GOD MODE (Supercond.)"
    
    # B. GEOMETRIC IMPEDANCE (Density Mismatch)
    # Штраф за разницу объемов
    vol_ratio = candidate['Vol'] / substrate['Vol']
    diff_pct = abs(1 - vol_ratio)
    
    # Коэффициент строгости (в плотных мирах строже)
    k_geo = 40.0
    if substrate['Vol'] < 8.0: k_geo = 50.0 # Dense World Penalty
    if substrate['Vol'] > 12.0: k_geo = 30.0 # Fluffy World Relax
    
    pen_dens = diff_pct * k_geo
    
    # C. WETTING BONUS (Plasticity)
    # Чем меньше Yield, тем лучше смачивание.
    # Но на холоде (Temp -> 0) пластичность падает.
    
    # Эмуляция "замерзания" пластичности
    yield_eff = candidate['Yield']
    if temp_k < 50:
        yield_eff = candidate['Yield'] * 2.0 # Harder when cold
    elif temp_k > 500:
        yield_eff = candidate['Yield'] * 0.5 # Softer when hot
        
    # Формула смачивания (ограничена 30 баллами)
    bonus_wet = min(500.0 / (yield_eff + 0.1), 30.0)
    
    # D. ARMOR BONUS (Oxide)
    bonus_armor = 0.0
    if candidate['OxideArmor']:
        bonus_armor = 15.0 # Tunneling stability bonus
    
    # E. NOISE PENALTY (Thermal)
    # Штраф за искажение решетки, усиленный температурой
    pen_noise = 0.0
    if candidate['Lat'] == 'HCP' or candidate['Lat'] == 'TET':
        # Гексагональные/Тетрагональные хуже стыкуются с Кубическими (BCC/FCC)
        if substrate['Lat'] in ['BCC', 'FCC']:
            base_noise = 10.0
            thermal_amp = temp_k / 300.0
            pen_noise = base_noise * thermal_amp

    # --- FINAL SCORE CALCULATION ---
    # База 90 (чтобы дать запас для бонусов)
    raw_score = 90.0 - pen_dens + bonus_wet + bonus_armor - pen_noise
    
    # Clipping
    final_score = max(0.0, min(raw_score, 100.0))
    
    # Verdict logic
    verdict = "Stable"
    if final_score > 95: verdict = "Perfect Resonance"
    elif final_score < 40: verdict = "Impedance Mismatch"
    elif final_score < 60: verdict = "Weak Interface"
    
    return final_score, verdict

# --- 3. UI LAYOUT ---

st.title("⚛️ Simureality: Geometric Interface Screener")
st.markdown("""
**Инструмент для быстрого поиска совместимых материалов на основе Геометрического Импеданса и Предела Текучести.**
*Основано на теории Simureality (v18).*
""")

# --- SIDEBAR (SETTINGS) ---
st.sidebar.header("🔬 Environment Conditions")
temp_k = st.sidebar.slider("Temperature (K)", min_value=0, max_value=1000, value=300, step=10)
priority = st.sidebar.selectbox("Optimization Goal", ["General Stability", "Cryogenic (Superconduction)", "High-Temp Strength"])

st.sidebar.divider()
st.sidebar.info(f"**Current Regime:** {temp_k}K")
if temp_k < 20:
    st.sidebar.success("❄️ QUANTUM REGIME DETECTED")
elif temp_k > 600:
    st.sidebar.warning("🔥 HIGH ENTROPY REGIME")

# --- MAIN TABS ---
tab1, tab2 = st.tabs(["🔍 Single Interface Check", "🌌 SCAN UNIVERSE (Matrix)"])

# === TAB 1: SINGLE CHECK ===
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Substrate (Core)")
        sub_name = st.selectbox("Select Core Material", df['Name'] + " (" + df['El'] + ")", index=0)
        sub_el = sub_name.split("(")[1].replace(")", "")
        sub_data = df[df['El'] == sub_el].iloc[0]
        
        st.metric("Core Volume", f"{sub_data['Vol']} Å³")
        st.metric("Core Yield", f"{sub_data['Yield']} MPa")
        
    with col2:
        st.subheader("2. Candidate (Coating)")
        cand_name = st.selectbox("Select Candidate Material", df['Name'] + " (" + df['El'] + ")", index=1)
        cand_el = cand_name.split("(")[1].replace(")", "")
        cand_data = df[df['El'] == cand_el].iloc[0]
        
        st.metric("Cand Volume", f"{cand_data['Vol']} Å³", delta=f"{cand_data['Vol'] - sub_data['Vol']:.2f}")
        st.metric("Cand Yield", f"{cand_data['Yield']} MPa")

    st.divider()
    
    if st.button("CALCULATE INTERFACE ENERGY", type="primary"):
        score, verdict = calculate_compatibility(sub_data, cand_data, temp_k, priority)
        
        st.subheader("Results")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            if score > 990:
                st.metric("Simureality Score", "∞", "GOD MODE")
            else:
                st.metric("Simureality Score", f"{score:.1f}/100")
        
        with c2:
            st.info(f"**Verdict:** {verdict}")
            if score > 990:
                st.success("Quantum Superconduction Achieved! Lattice is transparent to electron flow.")
            elif score > 90:
                st.success("Excellent wetting and geometric match. Recommended for critical contacts.")
            elif score < 40:
                st.error("High acoustic impedance reflection. Structural failure likely.")
                
        # Explanation
        st.markdown("### Why?")
        vol_mismatch = abs(1 - cand_data['Vol']/sub_data['Vol']) * 100
        st.write(f"- **Volume Mismatch:** {vol_mismatch:.1f}%")
        st.write(f"- **Wetting Ability:** {'High' if cand_data['Yield'] < 50 else 'Low'} ({cand_data['Yield']} MPa)")
        st.write(f"- **Thermal Noise:** {temp_k/300:.2f}x Baseline")

# === TAB 2: SCAN UNIVERSE ===
with tab2:
    st.header("🌌 Material Compatibility Matrix")
    st.markdown("Сканирование всех возможных пар материалов для выбранного Ядра.")
    
    target_core_name = st.selectbox("Select Substrate for Mass Scan", df['Name'] + " (" + df['El'] + ")", index=0)
    target_core_el = target_core_name.split("(")[1].replace(")", "")
    target_core = df[df['El'] == target_core_el].iloc[0]
    
    if st.button("RUN SCAN"):
        results = []
        
        # Progress bar simulation
        progress_text = "Scanning quantum lattice interactions..."
        my_bar = st.progress(0, text=progress_text)
        
        total = len(df)
        for i, (index, candidate) in enumerate(df.iterrows()):
            # Skip self
            if candidate['El'] == target_core['El']: continue
            
            s, v = calculate_compatibility(target_core, candidate, temp_k, priority)
            
            # Logic explanation for table
            reason = "Geometry"
            if candidate['Yield'] < 50: reason = "Plasticity (Wetting)"
            if s > 990: reason = "SUPERCONDUCTIVITY"
            if abs(1 - candidate['Vol']/target_core['Vol']) > 0.5: reason = "Density Mismatch"
            
            results.append({
                "Element": candidate['El'],
                "Name": candidate['Name'],
                "Score": s if s < 101 else 110, # Cap visual score for sorting
                "Display_Score": f"{s:.1f}" if s < 990 else "GOD",
                "Vol": candidate['Vol'],
                "Yield": candidate['Yield'],
                "Mechanism": reason
            })
            my_bar.progress((i + 1) / total)
            
        my_bar.empty()
        
        # Create DataFrame
        res_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
        
        # Color coding function
        def color_score(val):
            if val == "GOD": return "background-color: #8A2BE2; color: white" # Violet
            try:
                v = float(val)
                if v > 90: return "background-color: #28a745; color: white" # Green
                if v < 40: return "background-color: #dc3545; color: white" # Red
                if v < 70: return "background-color: #ffc107; color: black" # Yellow
            except: pass
            return ""

        # Show Table
        st.dataframe(
            res_df[["Element", "Name", "Display_Score", "Mechanism", "Vol", "Yield"]].style.map(color_score, subset=["Display_Score"]),
            use_container_width=True,
            height=600
        )
        
        # Heatmap Plot
        st.subheader("Visual Distribution")
        fig = px.scatter(res_df, x="Vol", y="Score", color="Mechanism", hover_data=["Name"],
                         title=f"Compatibility Spectrum for {target_core['Name']} Universe",
                         labels={"Vol": "Atomic Volume (Å³)", "Score": "Simureality Score"})
        # Add vertical line for Core Volume
        fig.add_vline(x=target_core['Vol'], line_dash="dash", line_color="red", annotation_text="Core Vol")
        st.plotly_chart(fig, use_container_width=True)
