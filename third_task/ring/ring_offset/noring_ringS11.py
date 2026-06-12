import matplotlib.pyplot as plt
import skrf as rf
import re
from pathlib import Path

dossier = Path(".")

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

def extraire_y_offset(chemin: Path) -> str | None:
	with chemin.open("r", encoding="utf-8", errors="ignore") as handle:
		for _ in range(40):
			ligne = handle.readline()
			if not ligne:
				break
			if "Parameters" not in ligne:
				continue
			match = re.search(r"y_offset=([^;]+)", ligne)
			if match:
				return match.group(1).strip()
	return None

fichiers = lister_fichiers_touchstone(dossier)
if not fichiers:
	raise FileNotFoundError("Aucun fichier touchstone trouve dans le dossier.")

fichier_ref = dossier / "sparams0.s2p"
if not fichier_ref.exists():
	raise FileNotFoundError("Fichier sparams0.s2p introuvable dans le dossier.")

fig, ax = plt.subplots(figsize=(11, 6))

freq_min = None
freq_max = None

fichier_offset = None
for chemin in fichiers:
	if chemin.name == fichier_ref.name:
		continue
	y_offset_valeur = extraire_y_offset(chemin)
	if y_offset_valeur is None:
		continue
	try:
		y_offset_float = float(y_offset_valeur)
	except ValueError:
		continue
	if abs(y_offset_float - (-3.0)) < 1e-6:
		fichier_offset = chemin
		break

if fichier_offset is None:
	raise FileNotFoundError("Aucun fichier avec y_offset=-3 trouve dans le dossier.")

reseau_ref = charger_touchstone(fichier_ref)
freq_ref = reseau_ref.f / 1e9
s11_ref = reseau_ref.s_db[:, 0, 0]
ax.plot(freq_ref, s11_ref, linewidth=2.2, color="#1f77b4", label="no ring")

reseau_offset = charger_touchstone(fichier_offset)
freq_offset = reseau_offset.f / 1e9
s11_offset = reseau_offset.s_db[:, 0, 0]
ax.plot(
	freq_offset,
	s11_offset,
	linewidth=3.0,
	color="#d62728",
	label="y_offset=-3",
	zorder=5,
)

freq_min = min(freq_ref[0], freq_offset[0])
freq_max = max(freq_ref[-1], freq_offset[-1])

# indication line at -10dB
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S11 [dB]', fontsize=13)
ax.set_title('S11 Comparison: no ring vs ring', fontsize=14)
ax.grid(True, alpha=0.35)
ax.set_xlim(freq_min, freq_max)
ax.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig("S11_compare_all.png", dpi=150)
plt.show()