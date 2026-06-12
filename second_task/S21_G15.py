import re
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf  # type: ignore[import-not-found]
from pathlib import Path

dossier = Path("s21g15")
def extract_tcoupling(fichier):
    with open(fichier, 'r') as f:
        for ligne in f:
            match = re.search(r'tcoupling=([\d.]+)', ligne)
            if match:
                return float(match.group(1))
    return 0.0

fichiers = sorted(dossier.glob("model_15S21_time_*.s2p"), key=extract_tcoupling)

print(f"{len(fichiers)} fichiers trouvés")

reseaux = []
for fichier in fichiers:
    tcoupling = extract_tcoupling(fichier)

    reseau = rf.Network(str(fichier))
    
    reseaux.append({'label':    f"tcoupling = {tcoupling} mm", 'reseau': reseau})

    
fix, ax = plt.subplots(figsize=(11, 6))

couleurs = plt.cm.plasma(np.linspace(0.1, 0.9, len(reseaux)))

for item, couleur in zip(reseaux, couleurs):
    reseau = item['reseau']

    freq_ghz = reseau.f / 1e9

    s21_db = reseau.s_db[:, 1, 0]

    ax.plot(freq_ghz, s21_db, linewidth=1.8, label=item['label'])

    
# indication line at -10dB 
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S21 [dB]', fontsize=13)
ax.set_title('S21 Parameter Sweep', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(freq_ghz[0], freq_ghz[-1])
ax.set_ylim(-80, 0)
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout()
plt.savefig("S21_sweep_G15.png", dpi=150)
plt.show()