import numpy as np
import matplotlib.pyplot as plt

def analyze_quarks():
    # --- DATA (CODATA 2018 / PDG) ---
    # Mass in MeV
    me = 0.511
    
    quarks = {
        "Up":    {"mass": 2.2,    "err": 0.4},   # 2.2 +/- 0.4
        "Down":  {"mass": 4.7,    "err": 0.4},   # 4.7 +/- 0.4
        "Strange":{"mass": 95.0,   "err": 5.0},   # 95 +/- 5
        "Charm": {"mass": 1275.0, "err": 25.0},  # 1275 +/- 25
        "Bottom":{"mass": 4180.0, "err": 30.0},  # 4180 +/- 30
        "Top":   {"mass": 172760.0,"err": 300.0} # 172.76 +/- 0.3 GeV
    }
    
    # --- HYPOTHESIS: M = N^2 * me ---
    
    results = []
    
    print(f"{'Quark':<10} | {'Mass (MeV)':<12} | {'N (Float)':<10} | {'N (Int)':<8} | {'Pred. Mass':<12} | {'Error'}")
    print("-" * 75)
    
    for name, data in quarks.items():
        m = data['mass']
        # Solve for N: N = sqrt(M / me)
        n_float = np.sqrt(m / me)
        n_int = int(round(n_float))
        
        m_pred = (n_int ** 2) * me
        
        # Error calculation
        diff = m_pred - m
        # Is it within experimental error bounds?
        in_bounds = abs(diff) <= data['err']
        
        # Special check for Top (it's huge, relative error matters more)
        rel_err = abs(diff) / m * 100
        
        res = {
            "name": name,
            "n_int": n_int,
            "mass_real": m,
            "mass_pred": m_pred,
            "rel_err": rel_err
        }
        results.append(res)
        
        print(f"{name:<10} | {m:<12.1f} | {n_float:<10.3f} | {n_int:<8} | {m_pred:<12.3f} | {rel_err:.2f}%")

    # --- PLOTTING ---
    plt.figure(figsize=(10, 6))
    
    # Log-Log plot to show scaling
    ns = [r['n_int'] for r in results]
    ms = [r['mass_real'] for r in results]
    names = [r['name'] for r in results]
    
    # Theoretical line M = me * N^2
    x_line = np.linspace(1, 1000, 100)
    y_line = (x_line**2) * me
    
    plt.loglog(x_line, y_line, '--', color='gray', label=r'$M = m_e \cdot N^2$')
    plt.loglog(ns, ms, 'ro', markersize=8, label='Quarks')
    
    for i, txt in enumerate(names):
        plt.annotate(f"{txt} (N={ns[i]})", (ns[i], ms[i]), xytext=(10, -10), textcoords='offset points')

    plt.title('The Geometric Origin of Quark Masses', fontsize=14)
    plt.xlabel('Node Count (N)', fontsize=12)
    plt.ylabel('Mass (MeV)', fontsize=12)
    plt.grid(True, which="both", ls="-", alpha=0.4)
    plt.legend()
    
    filename = 'quark_mass_scaling.png'
    plt.savefig(filename)
    return filename

file_quarks = analyze_quarks()
