import matplotlib.pyplot as plt
import skrf as rf
import re
from pathlib import Path

dossier = Path(__file__).parent

def charger_touchstone(chemin: Path) -> rf.Network:
    suffixe = chemin.suffix.lower()
    if re.fullmatch(r"\.s\d+p", suffixe):
        return rf.Network(str(chemin), file_type="touchstone")

    fichier_temp = chemin.with_suffix(".s2p")
    cree_temp = False
    if not fichier_temp.exists():
        fichier_temp.write_bytes(chemin.read_bytes())
        cree_temp = True

    reseau = rf.Network(str(fichier_temp), file_type="touchstone")
    if cree_temp:
        fichier_temp.unlink()
    return reseau

def extraire_parametres(chemin: Path) -> dict:
    params = {}
    try:
        with chemin.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "! Parameters =" in line:
                    match = re.search(r"\{(.*)\}", line)
                    if match:
                        parts = match.group(1).split(";")
                        for part in parts:
                            if "=" in part:
                                k, v = part.split("=")
                                params[k.strip()] = v.strip()
                    break
    except Exception as e:
        print(f"Erreur lors de l'extraction des paramètres de {chemin.name}: {e}")
    return params

fichiers = sorted(list(dossier.glob("model_topology_*.s2p")))

if not fichiers:
    raise FileNotFoundError("Aucun fichier model_topology_*.s2p trouvé dans le dossier.")

# Analyse des paramètres pour identifier ceux qui changent
tous_params = [extraire_parametres(f) for f in fichiers]
clefs_diff = set()
if tous_params:
    toutes_clefs = set().union(*(p.keys() for p in tous_params))
    for k in toutes_clefs:
        valeurs = [p.get(k) for p in tous_params]
        if len(set(valeurs)) > 1:
            clefs_diff.add(k)

fig, ax = plt.subplots(figsize=(11, 6))

freq_min = None
freq_max = None

for chemin, params in zip(fichiers, tous_params):
    reseau = charger_touchstone(chemin)
    freq_ghz = reseau.f / 1e9
    s11_db = reseau.s_db[:, 0, 0]

    # Construction du label avec seulement les paramètres qui diffèrent
    if clefs_diff:
        label = ", ".join([f"{k}={params.get(k, 'N/A')}" for k in sorted(clefs_diff)])
    else:
        label = chemin.name

    ax.plot(freq_ghz, s11_db, linewidth=1.8, label=label)

    if freq_min is None or freq_ghz[0] < freq_min:
        freq_min = freq_ghz[0]
    if freq_max is None or freq_ghz[-1] > freq_max:
        freq_max = freq_ghz[-1]

# indication line at -10dB
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S11 [dB]', fontsize=13)
ax.set_title('S11 Comparison', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(freq_min, freq_max)
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout()
plt.savefig(dossier / "S11_compare_all.png", dpi=150)
print(f"Graphique S11 sauvegardé dans {dossier / 'S11_compare_all.png'}")
