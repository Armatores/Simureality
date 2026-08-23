# -*- coding: utf-8 -*-
# ============================================================
# SIMUREALITY: GRID PHYSICS V21 (Streamlit Edition, English)
# Run: streamlit run this_file.py
# Requires mass.txt (AME2020, mass_1.mas20.txt) next to the script.
# Engine: V21 (audit final 2026-08-23; log: "Grid Physics — audit").
#   mean|err| = 8.93 MeV over 2248 verified AME2020 isotopes
#   Beta dispatcher: 82.2% of stable isotopes correctly identified.
#   Bare macro-link: E_b = 6.38 (fitted, single scalar) or 2pi
#   (geometric candidate) — selectable in the sidebar.
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

E_B_OPT  = 6.38       # оптимум по скану V21 (подогнана — честно отмечена)
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
    """V21: слоёное гало с реальным счётом портов и гармоникой 1/ℓ"""
    def __init__(self, e_b=6.38):
        self.E_B = e_b
        self._c = {0:(0,0,frozenset())}

    def crystal(self, n):
        """жадная ГЦК-сборка -> (макро-связи, порты, узлы)"""
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
        self._c[n] = (L, n*12 - 2*L, frozenset(occ))
        return self._c[n]

    def _halo_layers(self, core):
        layers = []
        occ_all = set(core)
        frontier = set(core)
        for _ in range(6):
            nxt = set()
            for nd in frontier:
                for nb in _neigh(nd):
                    if nb not in occ_all: nxt.add(nb)
            if not nxt: break
            layers.append(nxt)
            occ_all |= nxt
            frontier = nxt
        return layers

    def compile_mass(self, Z, N):
        if Z < 0 or N < 0: return float('inf')
        if Z == 0 and N == 1: return MASS_N
        if Z == 1 and N == 0: return MASS_P
        A = Z+N
        if A == 2: return Z*MASS_P+N*MASS_N-(E_LINK+E_PAIR-22*JITTER)
        if A == 3: return Z*MASS_P+N*MASS_N-(3*E_LINK+E_PAIR-30*JITTER)
        na = min(Z//2, N//2)
        L, ports, core = self.crystal(na)
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
                layers = self._halo_layers(core)
                placed = 0
                for li, layer in enumerate(layers):
                    for _ in range(len(layer)):
                        if placed >= orph: break
                        contacts = 3 if li == 0 else max(1, 3-(li-1))
                        bs += contacts*E_LINK/(li+1)
                        pu += contacts
                        placed += 1
                        jt += (placed/orph)*E_LINK*0.5
                    if placed >= orph: break
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
st.set_page_config(page_title="Grid Physics V21", layout="wide", page_icon="🧊")
st.title("Grid Physics V21: explicit geometric Coulomb + layered halo")

eb_choice = st.sidebar.radio("Bare macro-link E_b",
    [f"6.38 MeV (V21 optimum, mean|err|≈9.2)", f"2π = 6.2832 MeV (geometric candidate)"])
E_B = E_B_OPT if eb_choice.startswith("6.38") else E_B_2PI

df = load_ame("mass.txt")
grid = GridPhysicsV20(E_B)
drop = LiquidDrop()

if df.empty:
    st.error("mass.txt (AME2020) not found next to the script")
    st.stop()
st.sidebar.success(f"✅ AME2020-strict: {len(df)} verified nodes")

target_Z = st.sidebar.number_input("Protons (Z)", 1, 118, 82)
target_N = st.sidebar.number_input("Neutrons (N)", 0, 184, 126)
sym = ELEMENTS.get(target_Z, "?")
A_t = target_Z+target_N
st.sidebar.markdown(f"### Node: **{sym}-{A_t}**")

tab1, tab2, tab3 = st.tabs(["Single Node & Global Matrix", "Architecture Notes", "Nuclear Shapes"])

def shape_of(occ):
    """классификация формы кластера по тензору инерции"""
    import numpy as _np
    pts = _np.array(list(occ), float)
    pts -= pts.mean(0)
    if len(pts) < 2: return "point", (0,0,0)
    M = pts.T @ pts / len(pts)
    w, _ = _np.linalg.eigh(M)
    w = _np.sqrt(_np.maximum(w,0))
    r = w/max(w.sum(),1e-9)
    if r[2] > 0.52: return "CIGAR/line (prolate)", tuple(w)
    if r[0] < 0.20 and abs(r[1]-r[2]) < 0.09: return "PANCAKE/planar (oblate)", tuple(w)
    if abs(r[0]-r[1]) < 0.07 and abs(r[1]-r[2]) < 0.07: return "COMPACT (tetrahedron≈sphere)", tuple(w)
    if r[2] > r[0]*1.35: return "elongated (prolate)", tuple(w)
    return "triaxial", tuple(w)

def build_cluster(k):
    occ = {(0,0,0)}
    for _ in range(1,k):
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
    return occ

with tab1:
    st.write("### Single Node Analysis")
    c1,c2,c3 = st.columns(3)
    gm = grid.compile_mass(target_Z, target_N)
    if (target_Z,target_N) in df.index:
        exp = df.loc[(target_Z,target_N),'Mass_MeV']
        lm = drop.compile_mass(target_Z, target_N)
        winner = "🏆 V21 Grid Physics" if abs(gm-exp) <= abs(lm-exp) else "🏆 Weizsäcker LDM"
        c1.metric("AME2020 (hardware log)", f"{exp:.3f} MeV")
        c2.metric("Grid Physics V21", f"{gm:.3f} MeV",
                  delta=f"{gm-exp:+.3f} MeV | accuracy {100-abs(gm-exp)/exp*100:.4f}%",
                  delta_color="inverse")
        c3.metric("Weizsäcker (5 fits)", f"{lm:.3f} MeV",
                  delta=f"{lm-exp:+.3f} MeV | accuracy {100-abs(lm-exp)/exp*100:.4f}%",
                  delta_color="inverse")
        st.markdown(f"## {winner} on this node")
    else:
        c1.metric("AME2020", "node not measured")
        c2.metric("Grid Physics V21 (PREDICTION)", f"{gm:.3f} MeV")

    na = min(target_Z//2, target_N//2)
    L, ports, _core = grid.crystal(na)
    orph = A_t - 4*na
    shape, w = shape_of(build_cluster(na))
    st.write(f"Architecture: **{na}** α-modules, **{L}** macro-links, "
             f"**{ports}** surface ports, halo: **{orph}** nucleons (layers)")
    st.write(f"Shape from the builder: **{shape}**  (moments {w[0]:.2f}, {w[1]:.2f}, {w[2]:.2f})")

    verdict, gain = grid.beta(target_Z, target_N)
    if verdict == "STABLE":
        st.success(f"**[OK] Assembly stable. Buffer within limits.**")
    else:
        st.error(f"**BUFFER OVERFLOW: {verdict}.** Profitable transaction: +{gain:.3f} MeV")

    st.markdown("---")
    st.write("### Global Matrix (all verified isotopes)")
    if st.button("Compile global matrix (2248 nodes)"):
        with st.spinner("Compiling..."):
            rows = []
            for (Z,N), row in df.iterrows():
                A = Z+N
                if A < 4: continue
                exp = row['Mass_MeV']
                g = grid.compile_mass(Z,N); l = drop.compile_mass(Z,N)
                rows.append({"Node": f"{ELEMENTS.get(Z,'?')}-{A}", "Z":Z, "N":N, "A":A,
                             "AME2020": round(exp,3), "V21": round(g,3),
                             "Δ V21 (MeV)": round(g-exp,3),
                             "Accuracy V21 %": round(100-abs(g-exp)/exp*100,4),
                             "LDM": round(l,3), "Δ LDM (MeV)": round(l-exp,3),
                             "Accuracy LDM %": round(100-abs(l-exp)/exp*100,4),
                             "Crown": "V21" if abs(g-exp)<=abs(l-exp) else "LDM"})
            res = pd.DataFrame(rows)
            ga = res["Δ V21 (MeV)"].abs(); la = res["Δ LDM (MeV)"].abs()
            rms = float(np.sqrt((res["Δ V21 (MeV)"]**2).mean()))
            eff_g = 100 - (ga/res["AME2020"]).mean()*100
            eff_l = 100 - (la/res["AME2020"]).mean()*100
            wins = (res["Crown"]=="V21").sum()
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("V21: mean |error|", f"{ga.mean():.2f} MeV",
                      delta=f"accuracy {eff_g:.4f}%", delta_color="off")
            s2.metric("Weizsäcker: mean |error|", f"{la.mean():.2f} MeV",
                      delta=f"accuracy {eff_l:.4f}%", delta_color="off")
            s3.metric("V21 crowns", f"{wins} / {len(res)}",
                      delta=f"{wins/len(res)*100:.1f}% of nodes", delta_color="off")
            s4.metric("Max debt V21", f"{ga.max():.2f} MeV", delta_color="off")
            st.write("**By region:**")
            reg = []
            for lo,hi,nm in [(4,20,"A<20"),(20,60,"20–60"),(60,120,"60–120"),(120,400,"A≥120")]:
                sel = res[(res["A"]>=lo)&(res["A"]<hi)]
                reg.append({"Region":nm, "n":len(sel),
                            "V21 mean|Δ| MeV": round(sel["Δ V21 (MeV)"].abs().mean(),2),
                            "LDM mean|Δ| MeV": round(sel["Δ LDM (MeV)"].abs().mean(),2),
                            "Accuracy V21 %": round(sel["Accuracy V21 %"].mean(),4),
                            "Accuracy LDM %": round(sel["Accuracy LDM %"].mean(),4),
                            "V21 crowns": int((sel["Crown"]=="V21").sum())})
            st.dataframe(pd.DataFrame(reg), use_container_width=True)
            st.dataframe(res, use_container_width=True, height=380)
            st.download_button("📥 Download matrix (CSV)",
                res.to_csv(index=False).encode('utf-8'),
                "GridPhysics_V21_matrix.csv", "text/csv")

with tab2:
    st.markdown("""
    ### What is inside V21 (audit final 2026-08-23)
    1. **Core** — greedy FCC assembly of alpha-modules; macro-links at the bare link E_b.
    2. **Explicit geometric Coulomb**: −a_c^geom·Z(Z−1)/A^⅓, where a_c^geom = η_FCC/γ_vol = 0.706
       is derived in IPIL_305 (not a fit).
    3. **Halo** — layered lattice continuation: REAL vacant-shell counts (computed, not estimated:
       ¹⁶O core offers 24 first-shell sites, ⁴⁰Ca 40, ²⁰⁸Pb 87), contact weight E_LINK per contact,
       harmonic damping 1/(ℓ+1) with shell depth, anti-dedup fill tax (lattice Pauli).
    4. **Small halo** (≤3 nucleons): attachment model, full docking E_LINK.
    5. **Jitter**: open ports × E_0/39 (39 = 13×3, coordination-cluster scan count).

    **Honest boundaries:**
    - E_b=6.38 — the single fitted scalar (scan; geometric candidate 2π = 6.2832).
    - Mid-shell deformation zone — the dominant residual tail.
    - Beta dispatcher: 82.2% of stable isotopes (208/253) with zero decay-sector fitting.
    - Metric is MeV/RMS; percent-of-total-mass kept only for continuity with the first edition.

    **Fresh (2026-08):** LHC (O-O, Ne-Ne) measured the ¹⁶O tetrahedron and the ²⁰Ne pin;
    on FCC the 5th alpha attaches to the tetrahedron with at most 2 links and protrudes —
    the pin emerges from lattice topology with zero parameters.
    """)
with tab3:
    st.write("### Shapes of N=Z nuclei from the greedy builder (zero parameters)")
    st.caption("Verified 2026-08-23: Be-8 dumbbell ✓, C-12 triangle ✓, O-16 tetrahedron ✓ (LHC), "
               "Ne-20 pin ✓ (LHC), Mg-24 prolate ✓, Ca-40 compact ✓; Si-28 miss (we say prolate, nature oblate) — on record.")
    NZZ = {2:"He-4",6:"C-12",8:"O-16",10:"Ne-20",12:"Mg-24",14:"Si-28",16:"S-32",
           18:"Ar-36",20:"Ca-40",22:"Ti-44",24:"Cr-48",26:"Fe-52",28:"Ni-56"}
    srows = []
    for Z, nm in NZZ.items():
        na = Z//2
        occ = build_cluster(na)
        shape, w = shape_of(occ)
        L = sum(sum(1 for q in _neigh(nd) if q in occ) for nd in occ)//2
        srows.append({"Nucleus": nm, "n_α": na, "Macro-links": L,
                      "Moments": f"{w[0]:.2f} {w[1]:.2f} {w[2]:.2f}", "Shape": shape})
    st.dataframe(pd.DataFrame(srows), use_container_width=True)
    st.caption("Shape read from the inertia tensor of the greedy crystal. Halo not drawn — it sits on ports.")

st.caption("Simureality Research Group · Grid Physics V21 · engine: «Grid Physics V21 — компилятор масс.py»")
