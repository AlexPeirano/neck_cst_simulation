import re
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path


def extract_tcoupling(fichier):
    with open(fichier, 'r') as f:
        for ligne in f:
            match = re.search(r'tcoupling=([\d.]+)', ligne)
            if match:
                return float(match.group(1))
    return 0.0

dossier = Path(".")
fichiers = sorted(dossier.glob("model_st_time_*.s2p"), key=extract_tcoupling)
couleurs = plt.cm.plasma(np.linspace(0.1, 0.9, len(fichiers)))

fig, (ax_s11, ax_S21) = plt.subplots(2, 1, figsize=(11, 9), sharex=True)

for fichier, couleur in zip(fichiers, couleurs):
    tcoupling = extract_tcoupling(fichier)
    label = f"tcoupling = {tcoupling} mm"
    reseau = rf.Network(str(fichier))

    freq_GHz = reseau.f / 1e9

    s11_dB = reseau.s_db[:, 0, 0]
    S21_dB = reseau.s_db[:, 1, 0]

    ax_s11.plot(freq_GHz, s11_dB, color=couleur, linewidth=1.8, label=label)
    
    ax_S21.plot(freq_GHz, S21_dB, color=couleur, linewidth=1.8, label=label)

ax_s11.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")
ax_S21.axhline(y=-3, color='black', linestyle='--', linewidth=1, label="-3dB")

ax_s11.set_ylabel('S11 [dB]', fontsize=13)
ax_s11.set_title('Parameter Sweep Tcoupling', fontsize=14)
ax_s11.legend(fontsize=9, loc='lower left')
ax_s11.grid(True, alpha=0.35)

ax_S21.set_ylabel('S21 [dB]', fontsize=13)
ax_S21.set_xlabel('Frequency [GHz]', fontsize=13)
ax_S21.legend(fontsize=9, loc='upper right')
ax_s11.grid(True, alpha=0.35)
ax_S21.set_xlim(freq_GHz[0], freq_GHz[-1])

plt.tight_layout()
plt.savefig("S11_S21_PS.png")
plt.close()
