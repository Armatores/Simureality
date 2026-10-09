# -*- coding: utf-8 -*-
"""
Molecular Geometry Calculator — Grid Physics / Simureality (Pavel Popov, Simureality Research Group, Kyiv)
Reproduces the zero-parameter bond-angle predictions of the port model for the whole tetrahedral family.
Run:  streamlit run "Molecular Geometry Calculator (Streamlit, Grid Physics).py"
Needs: streamlit, numpy, scipy, pandas  (pip install streamlit numpy scipy pandas)
"""
import numpy as np
import streamlit as st
import pandas as pd
from scipy.optimize import minimize_scalar, minimize

a0 = 0.529177  # Å

# ---------------- The port model core (zero fitted parameters) ----------------
def coulson_fb(theta_deg):
    """Coulson hybrid relation: bond s-fraction from the bond angle."""
    m = -1/np.cos(np.radians(theta_deg))
    return 1/(1+m)

def repulsion_C3v(theta_deg, w):
    """3 bonds + 1 lone pair (C3v). Weighted spherical repulsion functional."""
    c = np.cos(np.radians(theta_deg))
    pol = np.degrees(np.arccos(np.sqrt((2*c+1)/3)))   # bond polar angle from the anti-LP axis
    ang_bl = 180-pol
    return 3*w/(2*np.sin(np.radians(ang_bl)/2)) + 3/(2*np.sin(np.radians(theta_deg)/2))

def repulsion_C2v(vars_, w):
    """2 bonds + 2 lone pairs (C2v), cooperative hierarchy 1:w:w^2."""
    thH, thL = vars_
    thHL = np.degrees(np.arccos(np.clip(np.cos(np.radians(thH/2))*np.cos(np.radians(thL/2)),-1,1)))
    return (1/(2*np.sin(np.radians(thH)/2)) + w**2/(2*np.sin(np.radians(thL)/2))
            + 4*w/(2*np.sin(np.radians(thHL)/2)))

def loop_angle(Z, nb, r_bond):
    """The self-consistent loop: angle -> Coulson mix -> LP centroid -> weight -> angle."""
    theta = 109.47
    for _ in range(80):
        fb = coulson_fb(theta)
        nlp = 4-nb
        flp = (1 - nb*fb)/nlp if nlp>0 else 0.0
        r_lp = (5+flp)*a0/Z
        w = (1 + r_bond/r_lp)/2
        if nb==3:
            theta = minimize_scalar(repulsion_C3v, bounds=(95,120), args=(w,), method='bounded').x
        elif nb==2:
            r = minimize(repulsion_C2v, [theta,115], args=(w,), method='Nelder-Mead',
                         options={'xatol':1e-5,'fatol':1e-9})
            theta = r.x[0]
    return theta, w

# ---------------- The covered molecules (the preprint's whole level) ----------------
# (name, formula, Z_eff central, n_bonds, r_bond Å, measured angle°, note, hybridized?)
MOLECULES = [
 ("Water","H₂O",4.55,2,0.958,104.45,"sp³: 2 bonds + 2 lone pairs",True),
 ("Ammonia","NH₃",3.90,3,1.012,107.30,"sp³: 3 bonds + 1 lone pair",True),
 ("Methane","CH₄",3.25,4,1.090,109.47,"sp³: 4 bonds (exact by symmetry)",True),
 ("Hydronium","H₃O⁺",4.55,3,0.980,111.30,"charged, 3 bonds + 1 pair",True),
 ("Nitrogen trifluoride","NF₃",3.90,3,1.365,102.10,"long N–F bond",True),
 ("Oxygen difluoride","OF₂",4.55,2,1.405,103.10,"long O–F bond",True),
 ("Phosphine","PH₃",None,None,None,93.80,"period-3: pure p ports (inert pair)",False),
 ("Hydrogen sulfide","H₂S",None,None,None,92.10,"period-3: pure p ports",False),
 ("Arsine","AsH₃",None,None,None,91.80,"period-3: pure p ports",False),
]

@st.cache_data
def compute_all():
    rows=[]
    for nm,fml,Z,nb,r,meas,note,hyb in MOLECULES:
        if not hyb:
            pred = 90.0   # boundary rule: unhybridized pure-p ports -> 90°
        elif nb==4:
            pred = 109.47 # exact by symmetry
        else:
            pred,_ = loop_angle(Z,nb,r)
        rows.append({"Molecule":nm,"Formula":fml,"Model angle (°)":round(pred,2),
                     "Measured (°)":meas,"Deviation (%)":round((pred-meas)/meas*100,2),"Note":note})
    return pd.DataFrame(rows)

# ---------------- Streamlit page ----------------
st.set_page_config(page_title="Molecular Geometry Calculator — Grid Physics", layout="wide")
st.title("Molecular Geometry from Port Synchronization")
st.markdown("**Grid Physics / Simureality — Pavel Popov, Simureality Research Group, Kyiv**")
st.markdown("""
This calculator reproduces the **zero-parameter bond-angle predictions** of the *port model*
(preprint: *Molecular Geometry from Port Synchronization*). In the model, space is a face-centered
cubic information lattice, and a period-2 atom carries **four tetrahedral ports** occupied by bonds
or lone pairs. The molecular shape is the minimum of a port-repulsion functional. The lone-pair
weight is **not fitted** — it comes from a self-consistent loop:
the angle fixes the hybrid mix (Coulson's theorem), the mix fixes the lone-pair centroid
(hydrogenic radial profile), the centroid fixes the repulsion weight, and the weight fixes the angle.
""")

df = compute_all()
st.subheader("Full results — the whole tetrahedral family")
st.dataframe(df, use_container_width=True, hide_index=True)

core = df[df['Molecule'].isin(["Water","Ammonia","Methane"])]
st.metric("Core molecules (H₂O, NH₃, CH₄) — median |deviation|", f"{core['Deviation (%)'].abs().median():.2f} %")
hyb = df[df['Note'].str.contains('sp³|charged|bond', regex=True)]
st.caption("Hybridized period-2 set computed by the zero-parameter loop; methane is exact by symmetry; "
           "period-3 hydrides (PH₃, H₂S, AsH₃) follow the hybridization-boundary rule (pure-p ports ≈ 90°, residual named in the preprint).")

st.divider()
st.subheader("Watch the loop converge on one molecule")
sel = st.selectbox("Molecule", [m[0] for m in MOLECULES if m[7] and m[3] in (2,3)])
if sel:
    m = next(x for x in MOLECULES if x[0]==sel)
    nm,fml,Z,nb,r,meas,note,hyb = m
    theta=109.47; track=[]
    for it in range(40):
        fb=coulson_fb(theta); nlp=4-nb; flp=(1-nb*fb)/nlp if nlp>0 else 0.0
        r_lp=(5+flp)*a0/Z; w=(1+r/r_lp)/2
        if nb==3: theta=minimize_scalar(repulsion_C3v,bounds=(95,120),args=(w,),method='bounded').x
        else:
            rr=minimize(repulsion_C2v,[theta,115],args=(w,),method='Nelder-Mead',options={'xatol':1e-5,'fatol':1e-9}); theta=rr.x[0]
        track.append(theta)
        if len(track)>2 and abs(track[-1]-track[-2])<1e-6: break
    c1,c2,c3 = st.columns(3)
    c1.metric("Computed", f"{track[-1]:.2f}°"); c2.metric("Measured", f"{meas:.2f}°"); c3.metric("Deviation", f"{(track[-1]-meas)/meas*100:+.2f}%")
    st.line_chart(pd.DataFrame({"bond angle (°)":track}))
    st.caption("The self-consistent loop: each iteration feeds the angle through the Coulson mix, the lone-pair centroid and the weight, and re-minimizes the port repulsion until it locks.")

st.divider()
st.subheader("What this is (and is not)")
st.markdown("""
- **Zero fitted parameters.** The only inputs are the bond length, the atomic number, and Slater screening. Every angle below is *computed*, not fitted.
- **Hybridization boundary for free.** Period-2 atoms hybridize their ports; period-3 and heavier bond through pure p ports — so their angles sit near 90° (the inert-pair pattern), which the same rule predicts.
- **Honest limitations.** The fluorides (NF₃, OF₂) and the charged hydronium deviate by 2–4.5% — the loop's weight estimate grows on long/ionic bonds; the preprint states this. The model describes *structure* (angles), not dynamics.
- The framework's two rules are used together throughout: a fixed global computational budget and local complexity minimization.
""")
st.caption("Preprint: P. Popov, «Molecular Geometry from Port Synchronization: Zero-Parameter Bond Angles on the FCC Vacuum Lattice» (Zenodo, 2026).")
