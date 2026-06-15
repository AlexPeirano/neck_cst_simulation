import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path
from scipy.signal import find_peaks
import numpy as np

def charger_touchstone(chemin: Path) -> rf.Network:
    return rf.Network(str(chemin))

files = {"25% Graphite": Path("matching_medium_s/g25.s2p")
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

    # Trouver les pics d'adaptation (minima locaux de S11)
    # find_peaks cherche les maxima, on passe donc -s11_db
    peaks, _ = find_peaks(-s11_db)
    
    if len(peaks) > 0:
        peak_freqs = freq_ghz[peaks]
        peak_values = s11_db[peaks]
        
        # Trier pour obtenir les 3 plus bas
        sorted_indices = np.argsort(peak_values)
        top_indices = sorted_indices[:3]
        
        print(f"\nLes 3 pics d'adaptations les plus bas pour {label} :")
        for i in top_indices:
            print(f"Fréquence : {peak_freqs[i]:.4f} GHz, S11 : {peak_values[i]:.2f} dB")
            # Ajouter un marqueur sur le graphique
            ax.plot(peak_freqs[i], peak_values[i], "ro")
            ax.annotate(f"{peak_freqs[i]:.2f} GHz", 
                        (peak_freqs[i], peak_values[i]),
                        textcoords="offset points", 
                        xytext=(0, -15), 
                        ha='center', 
                        fontsize=8,
                        color='red')

    if freq_min is None or freq_ghz[0] < freq_min:
        freq_min = freq_ghz[0]
    if freq_max is None or freq_ghz[-1] > freq_max:
        freq_max = freq_ghz[-1]

# indication line at -10dB
ax.axhline(y=-10, color='black', linestyle='--', linewidth=1, label="-10dB")

ax.set_xlabel('Frequency [GHz]', fontsize=13)
ax.set_ylabel('S11 [dB]', fontsize=13)
ax.set_title('S11 of the best topology', fontsize=14)
ax.grid(True, alpha=0.35)
if freq_min is not None and freq_max is not None:
    ax.set_xlim(freq_min, freq_max)
ax.legend(fontsize=9, loc='upper right')

plt.tight_layout()
plt.savefig("S11_goodmodel", dpi=150)
print("Graphique S11 sauvegardé dans S11_goodmodel.png")
