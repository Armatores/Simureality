import itertools
import pandas as pd
import streamlit as st

# --- SIMUREALITY CONSTANTS ---
MASS_P = 938.272
MASS_N = 939.565

ELEMENTS = {
    0: "n",
    1: "H",
    2: "He",
    3: "Li",
    4: "Be",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    10: "Ne",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    18: "Ar",
    19: "K",
    20: "Ca",
    21: "Sc",
    22: "Ti",
    23: "V",
    24: "Cr",
    25: "Mn",
    26: "Fe",
    27: "Co",
    28: "Ni",
    29: "Cu",
    30: "Zn",
    31: "Ga",
    32: "Ge",
    33: "As",
    34: "Se",
    35: "Br",
    36: "Kr",
    37: "Rb",
    38: "Sr",
    39: "Y",
    40: "Zr",
    41: "Nb",
    42: "Mo",
    43: "Tc",
    44: "Ru",
    45: "Rh",
    46: "Pd",
    47: "Ag",
    48: "Cd",
    49: "In",
    50: "Sn",
    51: "Sb",
    52: "Te",
    53: "I",
    54: "Xe",
    55: "Cs",
    56: "Ba",
    57: "La",
    58: "Ce",
    59: "Pr",
    60: "Nd",
    61: "Pm",
    62: "Sm",
    63: "Eu",
    64: "Gd",
    65: "Tb",
    66: "Dy",
    67: "Ho",
    68: "Er",
    69: "Tm",
    70: "Yb",
    71: "Lu",
    72: "Hf",
    73: "Ta",
    74: "W",
    75: "Re",
    76: "Os",
    77: "Ir",
    78: "Pt",
    79: "Au",
    80: "Hg",
    81: "Tl",
    82: "Pb",
    83: "Bi",
    84: "Po",
    85: "At",
    86: "Rn",
    87: "Fr",
    88: "Ra",
    89: "Ac",
    90: "Th",
    91: "Pa",
    92: "U",
    93: "Np",
    94: "Pu",
    95: "Am",
    96: "Cm",
    97: "Bk",
    98: "Cf",
    99: "Es",
    100: "Fm",
}


# --- 1. AME2020 PARSER ---
@st.cache_data
def load_ame_masses(filename="mass.txt"):
  data = []
  try:
    with open(filename, "r", encoding="utf-8") as f:
      for line in f:
        if len(line) < 65 or "N-Z" in line or "keV" in line:
          continue
        try:
          n_str, z_str, a_str = (
              line[5:10].strip(),
              line[10:15].strip(),
              line[15:19].strip(),
          )
          be_str = line[54:65].strip().replace("#", "").replace("*", "")
          if not n_str or not z_str or not be_str:
            continue
          N, Z, A = int(n_str), int(z_str), int(a_str)
          total_be_MeV = (float(be_str) * A) / 1000.0
          exp_nucleus_mass = (Z * MASS_P) + (N * MASS_N) - total_be_MeV
          data.append({"Z": Z, "N": N, "Mass_MeV": exp_nucleus_mass})
        except ValueError:
          continue
    df = pd.DataFrame(data)
    if not df.empty:
      df.set_index(["Z", "N"], inplace=True)
      df = df[~df.index.duplicated(keep="first")]
    return df
  except Exception as e:
    return pd.DataFrame(), str(e)


# --- 2. HARDWARE CACHE LIBRARY ---
CORE_BLOCKS = [
    (0, 1, "n"),
    (1, 0, "p"),
    (0, 2, "2n"),
    (1, 1, "H-2"),
    (1, 2, "H-3"),
    (2, 1, "He-3"),
    (2, 2, "He-4"),
    (2, 4, "He-6"),
    (3, 3, "Li-6"),
    (3, 4, "Li-7"),
    (4, 4, "Be-8"),
    (4, 5, "Be-9"),
    (5, 5, "B-10"),
    (6, 6, "C-12"),
    (7, 7, "N-14"),
    (8, 8, "O-16"),
    (10, 10, "Ne-20"),
    (12, 12, "Mg-24"),
    (14, 14, "Si-28"),
    (16, 16, "S-32"),
    (18, 18, "Ar-36"),
    (20, 20, "Ca-40"),
    (26, 30, "Fe-56"),
]

# --- STREAMLIT UI ---
st.set_page_config(page_title="Simureality Interface Debugger", layout="wide")
st.title("🌌 Grid Physics: Visual Interface Debugger")

df_masses = load_ame_masses("mass.txt")

if isinstance(df_masses, tuple) or df_masses.empty:
  st.error(
      "❌ Ошибка: файл `mass.txt` не найден в корневой директории проекта или"
      " поврежден! Положи его рядом с app.py."
  )
  st.stop()

# Build block mass dictionary
block_masses = {}
for z, n, name in CORE_BLOCKS:
  if z == 1 and n == 0:
    block_masses[name] = MASS_P
  elif z == 0 and n == 1:
    block_masses[name] = MASS_N
  elif z == 0 and n == 2:
    block_masses[name] = 2 * MASS_N - 0.5
  else:
    if (z, n) in df_masses.index:
      block_masses[name] = df_masses.loc[(z, n), "Mass_MeV"]

st.sidebar.header("Target Nucleus Selector")
target_Z = st.sidebar.number_input(
    "Protons (Z)", min_value=1, max_value=100, value=3, step=1
)
target_N = st.sidebar.number_input(
    "Neutrons (N)", min_value=1, max_value=160, value=8, step=1
)
target_A = target_Z + target_N
symbol = ELEMENTS.get(target_Z, "Unknown")
target_name = f"{symbol}-{target_A}"

max_blocks = st.sidebar.slider("Max Blocks to Merge", 2, 6, 4)

st.write(f"### Decompiling: **{target_name}** (Z={target_Z}, N={target_N})")

if (target_Z, target_N) in df_masses.index:
  target_mass = df_masses.loc[(target_Z, target_N), "Mass_MeV"]
  st.success(f"Empirical Mass (AME2020): **{target_mass:.4f} MeV**")

  with st.spinner("Calculating valid topological fusion paths..."):
    available_blocks = [
        (z, n, name)
        for z, n, name in CORE_BLOCKS
        if name in block_masses and (z != target_Z or n != target_N)
    ]
    valid_paths = []

    for k in range(2, max_blocks + 1):
      for combo in itertools.combinations_with_replacement(available_blocks, k):
        sum_z = sum(b[0] for b in combo)
        sum_n = sum(b[1] for b in combo)
        if sum_z == target_Z and sum_n == target_N:
          path_names = [b[2] for b in combo]
          sum_mass = sum(block_masses[name] for name in path_names)
          interface_energy = sum_mass - target_mass
          valid_paths.append({
              "Path": " + ".join(path_names),
              "Blocks": k,
              "Total Initial Mass": round(sum_mass, 4),
              "Interface Energy (MeV)": round(interface_energy, 4),
          })

  if valid_paths:
    df_results = pd.DataFrame(valid_paths).sort_values(
        by="Interface Energy (MeV)", ascending=False
    )
    st.markdown(f"Found **{len(df_results)}** valid geometric assembly paths:")
    st.dataframe(df_results, use_container_width=True)

    best_path = df_results.iloc[0]
    st.info(
        f"**Highest Deduplication Profit:** \n\n`{best_path['Path']}  ⟶ "
        f" {target_name}` \n\nMatrix saves **{best_path['Interface Energy (MeV)']}"
        " MeV** in this macro-link."
    )
  else:
    st.warning(
        "No exact block combinations found with current limits. Try increasing"
        " 'Max Blocks'."
    )
else:
  st.warning(
      f"Nucleus {target_name} (Z={target_Z}, N={target_N}) not found in loaded"
      " AME database."
  )
