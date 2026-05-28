import matplotlib.pyplot as plt
import skrf as rf
import re
from pathlib import Path

dossier = Path(__file__).parent / "data"

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

def lister_fichiers_touchstone(dossier: Path) -> list[Path]:
	fichiers = []
	for chemin in sorted(dossier.iterdir()):
		if not chemin.is_file():
			continue
		suffixe = chemin.suffix.lower()
		if re.fullmatch(r"\.s\d+p", suffixe):
			fichiers.append(chemin)
	return fichiers

def extraire_rm(chemin: Path) -> str | None:
	with chemin.open("r", encoding="utf-8", errors="ignore") as handle:
		for _ in range(40):
			ligne = handle.readline()
			if not ligne:
				break
			if "Parameters" not in ligne:
				continue
			match = re.search(r"Ls=([^;]+)", ligne)
			if match:
				return match.group(1).strip()
	return None

fichiers_s2p = sorted(list(dossier.glob("model_topology_*.s2p")))
# On prend les deux derniers (runs 7 et 8 par exemple)
fichiers = fichiers_s2p[-2:]

if not fichiers:
	raise FileNotFoundError("Aucun fichier model_topology_*.s2p trouve dans le dossier.")

fig, ax = plt.subplots(figsize=(11, 6))

freq_min = None
freq_max = None

for chemin in fichiers:
	reseau = charger_touchstone(chemin)
	freq_ghz = reseau.f / 1e9
	s21_db = reseau.s_db[:, 1, 0]

	# Extraction du numéro de run depuis le nom du fichier
	match = re.search(r"_(\d+)_(\d+)\.s2p$", chemin.name)
	run_num = match.group(1) if match else None

	if run_num == "1":
		label = "initial ring topology"
	elif run_num == "8":
		label = "optimized ring topology"
	else:
		label = chemin.name

	ax.plot(freq_ghz, s21_db, linewidth=1.8, label=label)


	if freq_min is None or freq_ghz[0] < freq_min:
		freq_min = freq_ghz[0]
	if freq_max is None or freq_ghz[-1] > freq_max:
		freq_max = freq_ghz[-1]



ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S21 [dB]', fontsize=13)
ax.set_title('S21 Comparison', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(freq_min, freq_max)
ax.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig("S21_u", dpi=150)
# plt.show()1_u.png", dpi=150)
# plt.show()