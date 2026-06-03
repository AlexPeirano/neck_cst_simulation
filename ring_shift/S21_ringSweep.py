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

def lister_fichiers_touchstone(dossier: Path) -> list[Path]:
	fichiers = []
	for chemin in sorted(dossier.iterdir()):
		if not chemin.is_file():
			continue
		suffixe = chemin.suffix.lower()
		if re.fullmatch(r"\.s\d+p", suffixe):
			fichiers.append(chemin)
	return fichiers

def extraire_params(chemin: Path) -> dict:
	params = {"Rm": "N/A", "Tcouple": "N/A", "wslot": "N/A"}
	with chemin.open("r", encoding="utf-8", errors="ignore") as f:
		for line in f:
			if "! Parameters =" in line:
				m_rm = re.search(r"R_m=([^;{}]+)", line)
				m_tc = re.search(r"tcoupling=([^;{}]+)", line)
				m_ws = re.search(r"w_slot=([^;{}]+)", line)
				if m_rm: params["Rm"] = m_rm.group(1).strip()
				if m_tc: params["Tcouple"] = m_tc.group(1).strip()
				if m_ws: params["wslot"] = m_ws.group(1).strip()
				break
	return params

fichiers = sorted(list(dossier.glob("ring_shit_*.s2p")), key=lambda x: int(re.search(r"(\d+)", x.name).group(1)) if re.search(r"(\d+)", x.name) else x.name)

if not fichiers:
	raise FileNotFoundError("Aucun fichier ring_shit_*.s2p trouve dans le dossier.")

fig, ax = plt.subplots(figsize=(11, 6))

freq_min = None
freq_max = None

# Paramètres cibles
cibles = [
    {"Rm": "6.5", "Tc": "4", "ws": "0.2"},
    {"Rm": "4.5", "Tc": "4", "ws": "0.5"},
    {"Rm": "5.5", "Tc": "4", "ws": "0.3"}
]

for chemin in fichiers:
	p = extraire_params(chemin)
	
	# Vérification si le fichier correspond à une des cibles
	match = False
	for c in cibles:
		if (p["Rm"] == c["Rm"] and 
			p["Tcouple"] == c["Tc"] and 
			p["wslot"] == c["ws"]):
			match = True
			break
	
	if not match:
		continue

	reseau = charger_touchstone(chemin)
	freq_ghz = reseau.f / 1e9
	s21_db = reseau.s_db[:, 1, 0]

	label = f"Rm={p['Rm']}, Tc={p['Tcouple']}, ws={p['wslot']}"

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
ax.legend(fontsize=9, loc='best')

plt.tight_layout()
plt.savefig("S21_ring_shift", dpi=150)
# plt.show()
