# -*- coding: utf-8 -*-
# ============================================================
# SIMUREALITY: GRID PHYSICS V20 (Streamlit Edition)
# Покрутить самому: streamlit run этот_файл.py
# Нужен mass.txt (AME2020, mass_1.mas20.txt) рядом со скриптом.
# Движок: финал аудита 2026-08-22 (лог: "Grid Physics — аудит...").
#   mean|Δ| = 13.07 MeV по 2248 проверенным изотопам AME2020
#   Бета-диспетчер: 81.4% стабильных опознаны верно.
#   Голый линк: E_b = 6.45 (оптимум) или 2π=6.2832 (кандидат
#   из геометрии) — переключается в сайдбаре.
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np

# --- АППАРАТНЫЕ КОНСТАНТЫ (все выведены, кроме отмеченной) ---
MASS_P, MASS_N = 938.272, 939.565
E_ALPHA  = 28.32      # 12*E_LINK (выведена, IPIL_305)
E_LINK   = 2.36       # 4*m_e*γ_lin (выведена)
E_PAIR   = 1.18       # E_LINK/2
JITTER   = 0.01311    # E_LINK/180
A_CG     = 0.706      # η_FCC/γ_vol (выведена, IPIL_305)
E_EL     = 0.511

E_B_OPT  = 6.45       # оптимум по скану (подогнана — честно отмечена)
E_B_2PI  = 2*np.pi    # геометрический кандидат (калибровка Ca-40: 6.281)

# --- Вейцзеккер (5 фитов, для сравнения) ---
A_V, A_S, A_C, A_A, A_P = 15.75, 17.8, 0.711, 23.7, 11.18

ELEMENTS = {0:'n',1:'H',2:'He',3:'Li',4:'Be',5:'B',6:'C',7:'N',8:'O',9:'F',10:'Ne',
    11:'Na',12:'Mg',13:'Al',14:'Si',15:'P',16:'S',17:'Cl',18:'Ar',19:'K',20:'Ca',
    21:'Sc',22:'Ti',23:'V',24:'Cr',25:'Mn',26:'Fe',27:'Co',28:'Ni',29:'Cu',30:'Zn',
    31:'Ga',32:'Ge',33:'As',34:'Se',35:'Br',36:'Kr',37:'Rb',38:'Sr',39:'Y',40:'Zr',
    41:'Nb',42:'Mo',43:'Tc',44:'Ru',45:'Rh',46:'Pd',47:'Ag',48:'Cd',49:'In',50:'Sn',
    51:'Sb',52:'Te',53:'I',54:'Xe',55:'Cs',56:'Ba',57:'La',58:'Ce',59:'Pr',60:'Nd',
    61:'Pm',62:'Sm',63:'Eu',64:'Gd',65:'Tb',66:'Dy',67:'Ho',68:'Er',69:'Tm',70:'Yb',
    71:'Lu',72:'Hf',73:'Ta',74:'W',75:'Re',76:'Os',77:'Ir',78:'Pt',79:'Au',80:'Hg',
    81:'Tl',82:'Pb',83:'Bi',84:'Po',85:'At',86:'Rn',87:'Fr',88:'Ra',89:'Ac',90:'Th',
    91:'Pa',92:'U',93:'Np',94:'Pu',95:'Am',96:'Cm',97:'Bk',98:'Cf',99:'Es',100:'Fm',
    101:'Md',102:'No',103:'Lr',104:'Rf',105:'Db',106:'Sg',107:'Bh',108:'Hs'}

NEI = [(1,1,0),(1,-1,0),(-1,1,0),(-1,-1,0),(1,0,1),(1,0,-1),
       (-1,0,1),(-1,0,-1),(0,1,1),(0,1,-1),(0,-1,1),(0,-1,-1)]

def _neigh(n):
    x,y,z = n
    return [(x+dx,y+dy,z+dz) for dx,dy,dz in NEI]

class GridPhysicsV20:
    def __init__(self, e_b=6.45):
        self.E_B = e_b
        self._c = {0:(0,0),1:(0,12),2:(1,22),3:(3,30),4:(6,36)}

    def crystal(self, n):
        """жадная ГЦК-сборка -> (макро-связи, поверхностные порты)"""
        if n in self._c: return self._c[n]
        occ = {(0,0,0)}
        for _ in range(1,n):
            cand = set()
            for nd in occ:
                for nb in _neigh(nd):
                    if nb not in occ: cand.add(nb)
            cm = [sum(q[i] for q in occ)/len(occ) for i in range(3)]
            best, mb, md = None,-1,float('inf')
            for c in cand:
                b = sum(1 for q in _neigh(c) if q in occ)
                dsq = sum((c[i]-cm[i])**2 for i in range(3))
                if b > mb or (b == mb and dsq < md): mb, md, best = b, dsq, c
            occ.add(best)
        L = sum(sum(1 for q in _neigh(nd) if q in occ) for nd in occ)//2
        self._c[n] = (L, n*12 - 2*L)
        return self._c[n]

    def compile_mass(self, Z, N):
        if Z < 0 or N < 0: return float('inf')
        if Z == 0 and N == 1: return MASS_N
        if Z == 1 and N == 0: return MASS_P
        A = Z+N
        if A == 2: return Z*MASS_P+N*MASS_N-(E_LINK+E_PAIR-22*JITTER)
        if A == 3: return Z*MASS_P+N*MASS_N-(3*E_LINK+E_PAIR-30*JITTER)
        na = min(Z//2, N//2)
        L, ports = self.crystal(na)
        rZ, rN = Z-2*na, N-2*na
        orph = rZ+rN
        bs = na*E_ALPHA + L*self.E_B
        jt = 0.0; pu = 0
        if orph > 0:
            prs = min(rZ, rN)
            bs += prs*(E_LINK+E_PAIR)
            if orph <= 3:
                sl = 0 if orph==1 else (1 if orph==2 else 3)
                bs += (sl*(E_LINK/3.0) if prs==0 else max(0,sl-prs)*(E_LINK/3.0))
                if ports > 0:
                    dn = min(orph, ports)
                    bs += dn*E_LINK; pu = dn
            else:
                sc = na**(2/3)
                cd, ce = int(sc*2.0), int(sc*3.0)
                for _ in range(orph):
                    if cd>0 and (ports-pu)>=3:   bs += 3.0*E_LINK; pu += 3; cd -= 1
                    elif ce>0 and (ports-pu)>=2: bs += 2.0*E_LINK; pu += 2; ce -= 1
                    elif (ports-pu)>=1:          bs += 1.0*E_LINK; pu += 1
            jt += max(0, orph*12-pu)*JITTER + abs(rZ-rN)*JITTER*2.5
        coul = A_CG*Z*(Z-1)/(A**(1/3))
        return Z*MASS_P+N*MASS_N-(bs-jt)+coul

    def beta(self, Z, N):
        m0 = self.compile_mass(Z,N)
        m_bm = self.compile_mass(Z+1,N-1)+E_EL
        m_bp = self.compile_mass(Z-1,N+1)+E_EL
        if m_bm < m0: return "BETA− (GC)", m0-m_bm
        if m_bp < m0: return "BETA+ (GC)", m0-m_bp
        return "STABLE", 0.0

class LiquidDrop:
    def compile_mass(self, Z, N):
        A = Z+N
        if A < 2: return Z*MASS_P+N*MASS_N
        pr = A_P/A**0.5 if (Z%2==0 and N%2==0) else (-A_P/A**0.5 if (Z%2 and N%2) else 0)
        return (Z*MASS_P+N*MASS_N
                -(A_V*A - A_S*A**(2/3) - A_C*Z*(Z-1)/A**(1/3) - A_A*(A-2*Z)**2/A + pr))

@st.cache_data
def load_ame(filename="mass.txt"):
    """строгий парсер: теоретические строки (#, *) выбрасываются"""
    data = []
    try:
        with open(filename,'r',encoding='utf-8') as f:
            for line in f:
                if len(line) < 65 or 'N-Z' in line or 'keV' in line: continue
                if '#' in line or '*' in line: continue
                try:
                    N,Z,A = int(line[5:10]), int(line[10:15]), int(line[15:19])
                    be = float(line[54:65].strip())*A/1000.0
                    data.append({'Z':Z,'N':N,'Mass_MeV':Z*MASS_P+N*MASS_N-be})
                except ValueError: continue
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index(['Z','N'], inplace=True)
            df = df[~df.index.duplicated(keep='first')]
        return df
    except Exception:
        return pd.DataFrame()

# ============================ UI ============================
st.set_page_config(page_title="Grid Physics V20", layout="wide", page_icon="🧊")
st.title("Grid Physics V20: явный геометрический Кулон + полный скин")

eb_choice = st.sidebar.radio("Голый макро-линк E_b",
    [f"6.45 MeV (оптимум, mean|Δ|=13.07)", f"2π = 6.2832 MeV (геометрия, mean|Δ|≈18.1)"])
E_B = E_B_OPT if eb_choice.startswith("6.45") else E_B_2PI

df = load_ame("mass.txt")
grid = GridPhysicsV20(E_B)
drop = LiquidDrop()

if df.empty:
    st.error("mass.txt (AME2020) не найден рядом со скриптом")
    st.stop()
st.sidebar.success(f"✅ AME2020-strict: {len(df)} проверенных узлов")

target_Z = st.sidebar.number_input("Протоны (Z)", 1, 118, 82)
target_N = st.sidebar.number_input("Нейтроны (N)", 0, 184, 126)
sym = ELEMENTS.get(target_Z, "?")
A_t = target_Z+target_N
st.sidebar.markdown(f"### Узел: **{sym}-{A_t}**")

tab1, tab2 = st.tabs(["Одиночный узел & Глобальная матрица", "Архитектурные заметки"])

with tab1:
    st.write("### Анализ одиночного узла")
    c1,c2,c3 = st.columns(3)
    gm = grid.compile_mass(target_Z, target_N)
    if (target_Z,target_N) in df.index:
        exp = df.loc[(target_Z,target_N),'Mass_MeV']
        c1.metric("AME2020 (лог железа)", f"{exp:.3f} MeV")
        c2.metric("Grid Physics V20", f"{gm:.3f} MeV",
                  delta=f"{gm-exp:+.3f} MeV", delta_color="inverse")
        lm = drop.compile_mass(target_Z, target_N)
        c3.metric("Вейцзеккер (5 фитов)", f"{lm:.3f} MeV",
                  delta=f"{lm-exp:+.3f} MeV", delta_color="inverse")
    else:
        c1.metric("AME2020", "узел не измерен")
        c2.metric("Grid Physics V20 (ПРОГНОЗ)", f"{gm:.3f} MeV")

    na = min(target_Z//2, target_N//2)
    L, ports = grid.crystal(na)
    orph = A_t - 4*na
    st.write(f"Архитектура: **{na}** α-модулей, **{L}** макро-связей, "
             f"**{ports}** поверхностных портов, гало: **{orph}** нуклонов")

    verdict, gain = grid.beta(target_Z, target_N)
    if verdict == "STABLE":
        st.success(f"**[OK] Сборка стабильна. Буфер в норме.**")
    else:
        st.error(f"**BUFFER OVERFLOW: {verdict}.** Транзакция выгодна: +{gain:.3f} MeV")

    st.markdown("---")
    st.write("### Глобальная матрица (все проверенные изотопы)")
    if st.button("Скомпилировать глобальную матрицу (2248 узлов)"):
        with st.spinner("Компиляция..."):
            rows = []
            for (Z,N), row in df.iterrows():
                A = Z+N
                if A < 4: continue
                exp = row['Mass_MeV']
                g = grid.compile_mass(Z,N); l = drop.compile_mass(Z,N)
                rows.append({"Узел": f"{ELEMENTS.get(Z,'?')}-{A}", "Z":Z, "N":N, "A":A,
                             "AME2020": round(exp,3), "V20": round(g,3),
                             "Δ V20 (MeV)": round(g-exp,3),
                             "Вейцзеккер": round(l,3), "Δ LDM (MeV)": round(l-exp,3)})
            res = pd.DataFrame(rows)
            ga = res["Δ V20 (MeV)"].abs(); la = res["Δ LDM (MeV)"].abs()
            rms = float(np.sqrt((res["Δ V20 (MeV)"]**2).mean()))
            s1,s2,s3 = st.columns(3)
            s1.metric("V20: средняя |ошибка|", f"{ga.mean():.2f} MeV", delta=f"RMS {rms:.2f}", delta_color="off")
            s2.metric("Вейцзеккер: средняя |ошибка|", f"{la.mean():.2f} MeV", delta_color="off")
            s3.metric("Макс. долг V20", f"{ga.max():.2f} MeV", delta_color="off")
            st.write("**По регионам (V20, mean |Δ|, MeV):**")
            reg = []
            for lo,hi,nm in [(4,20,"A<20"),(20,60,"20–60"),(60,120,"60–120"),(120,400,"A≥120")]:
                sel = res[(res["A"]>=lo)&(res["A"]<hi)]
                reg.append({"Регион":nm, "n":len(sel),
                            "V20 mean|Δ|": round(sel["Δ V20 (MeV)"].abs().mean(),2),
                            "LDM mean|Δ|": round(sel["Δ LDM (MeV)"].abs().mean(),2)})
            st.dataframe(pd.DataFrame(reg), use_container_width=True)
            st.dataframe(res, use_container_width=True, height=380)
            st.download_button("📥 Скачать матрицу (CSV)",
                res.to_csv(index=False).encode('utf-8'),
                "GridPhysics_V20_matrix.csv", "text/csv")

with tab2:
    st.markdown("""
    ### Что внутри V20 (финал аудита 2026-08-22)
    1. **Ядро** — жадная ГЦК-сборка альфа-модулей; макро-связи голым линком E_b.
    2. **Кулон ЯВНО и геометрически**: −a_c^geom·Z(Z−1)/A^⅓, где a_c^geom = η_FCC/γ_vol = 0.706
       выведен в IPIL_305 (не фит).
    3. **Гало** — продолжение решётки с полным весом контакта: лунка 3·E_LINK (7.08 MeV ≈
       энергия отделения нейтрона), ребро 2·E_LINK, вершина E_LINK. (Находка аудита:
       изоспиновые 50% были ошибкой построения.)
    4. **Скин-нарост** (≤3 нуклона): полный докинг E_LINK.
    5. **Джиттер**: открытые порты × E_LINK/180 + асимметрия ×2.5.

    **Известные границы (честно):**
    - E_b=6.45 — единственный подогнанный скаляр (скан; геометрический кандидат 2π даёт 18.1 MeV).
    - Зона деформации (середины тяжёлых оболочек) — главный остаточный хвост.
    - Бета-диспетчер: 81.4% стабильных (206/253) без фитов под распады.
    - Метрика в MeV/RMS; «процент от полной массы» не используем — вводящая метрика.

    **Свежее (2026-08):** LHC (O-O, Ne-Ne) измерил ¹⁶O-тетраэдр и ²⁰Ne-пин;
    на ГЦК 5-я альфа к тетраэдру крепится максимум 2 связями и торчит наружу —
    пин возникает из решётки без параметров.
    """)

st.caption("Simureality Research Group · Grid Physics V20 · движок без стримлит-обёртки: «Grid Physics V20 — компилятор масс (финал).py»")
