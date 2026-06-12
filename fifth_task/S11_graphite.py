import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path

def charger_touchstone(chemin: Path) -> rf.Network:
    return rf.Network(str(chemin))

files = {"5% Graphite": Path("matching_medium_s/g5.s2p"),
"25% Graphite": Path("matching_medium_s/g25.s2p"),
"30% Graphite": Path("matching_medium_s/g30.s2p"),
}
fig, ax = plt.subplots(figsize=(11, 6))

freq_min = None
freq_max = None

for label, chemin in files.items():
    if not chemin.exists():
        print(f"Fichier non trouvé : {chemin}")
        continue
        
    reseau = charger_touchstone(chemin)
    freq_ghz = reseau.f / 1e9
    s11_db = reseau.s_db[:, 0, 0]

    ax.plot(freq_ghz, s11_db, linewidth=1.8, label=label)

    if freq_min is None or freq_ghz[0] < freq_min:
        freq_min = freq_ghz[0]
    if freq_max is None or freq_ghz[-1] > freq_max:
        freq_max = freq_ghz[-1]

# indication line at -10dB
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S11 [dB]', fontsize=13)
ax.set_title('S11 Comparison: Graphite percentage comparison', fontsize=14)
ax.grid(True, alpha=0.35)
if freq_min is not None and freq_max is not None:
    ax.set_xlim(freq_min, freq_max)
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout()
plt.savefig("S11_graphite", dpi=150)
print("Graphique S11 sauvegardé dans S11_thicker_necks.png")
