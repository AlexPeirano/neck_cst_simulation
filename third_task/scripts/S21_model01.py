import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path

dossier = Path(".")
fichier_model_1 = dossier / "optimizer_sparams_1.s2p"
fichier_model_2 = dossier / "optimizer_sparams_2.s2p"

reseau_1 = rf.Network(str(fichier_model_1))
reseau_2 = rf.Network(str(fichier_model_2))

fix, ax = plt.subplots(figsize=(11, 6))

freq_ghz_1 = reseau_1.f / 1e9
freq_ghz_2 = reseau_2.f / 1e9

s21_db_1 = reseau_1.s_db[:, 1, 0]
s21_db_2 = reseau_2.s_db[:, 1, 0]

ax.plot(freq_ghz_1, s21_db_1, linewidth=1.8, label="Model 1")
ax.plot(freq_ghz_2, s21_db_2, linewidth=1.8, label="Model 2")

    
# indication line at -10dB 
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S21 [dB]', fontsize=13)
ax.set_title('S21 Comparison', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(min(freq_ghz_1[0], freq_ghz_2[0]), max(freq_ghz_1[-1], freq_ghz_2[-1]))
ax.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig("S21_compare.png", dpi=150)
plt.show()