import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path

dossier = Path(".")
fichier_sparams_0 = dossier / "sparams0"
fichier_sparams_1 = dossier / "realoptimizer_2"

def charger_touchstone(chemin: Path) -> rf.Network:
	suffixe = chemin.suffix.lower()
	if suffixe.startswith(".s") and suffixe[2:].isdigit():
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

reseau_0 = charger_touchstone(fichier_sparams_0)
reseau_1 = charger_touchstone(fichier_sparams_1)

fig, ax = plt.subplots(figsize=(11, 6))

freq_ghz_0 = reseau_0.f / 1e9
freq_ghz_1 = reseau_1.f / 1e9

s11_db_0 = reseau_0.s_db[:, 0, 0]
s11_db_1 = reseau_1.s_db[:, 0, 0]

ax.plot(freq_ghz_0, s11_db_0, linewidth=1.8, label="First Model")
ax.plot(freq_ghz_1, s11_db_1, linewidth=1.8, label="Optimized Model")

    
# indication line at -10dB 
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S11 [dB]', fontsize=13)
ax.set_title('S11 Comparison', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(min(freq_ghz_0[0], freq_ghz_1[0]), max(freq_ghz_0[-1], freq_ghz_1[-1]))
ax.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig("S11_compare_final.png", dpi=150)
plt.show()