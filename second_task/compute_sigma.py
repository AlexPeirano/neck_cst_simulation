import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


eps_0 = 8.854e-12
fichier = str(Path(__file__).resolve().with_name("esp_prime_prime.txt"))

def extract_values(fichier):
    data_f = []
    data_eps = []
    with open(fichier, 'r') as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            parts = ligne.split('\t')
            if len(parts) < 2:
                parts = ligne.split()
            if len(parts) < 2:
                continue
            try:
                data_f.append(float(parts[0]))
                data_eps.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
    return np.array(data_f), np.array(data_eps)

def compute_sigma(data_eps, data_f_ghz):
    data_f_hz = np.asarray(data_f_ghz, dtype=float) * 1e9
    data_eps = np.asarray(data_eps, dtype=float)
    return 2 * np.pi * eps_0 * data_f_hz * data_eps
    
data_f, data_eps = extract_values(fichier)
if data_f.size == 0 or data_eps.size == 0:
    raise ValueError(f"No data parsed from {fichier}")

sigma = compute_sigma(data_eps, data_f)
mask = np.isfinite(data_f) & np.isfinite(sigma) & (data_f >= 0.5) & (data_f <= 3.5)
data_f = data_f[mask]
sigma = sigma[mask]
if data_f.size == 0:
    raise ValueError("All computed values are non-finite or outside frequency range")

print(sigma) 
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(data_f, sigma, linewidth=1.8, marker=".", markersize=3, label="sigma")
ax.set_xlim(data_f[0], data_eps[-1])
ax.set_ylabel("Conductivity", fontsize=13)
ax.set_xlabel("Frequency [GHz]", fontsize=13)
ax.set_title("Conductivity vs Frequency", fontsize=14)
ax.legend(fontsize=9, loc='lower left')

plt.tight_layout()
plt.savefig("sigma.png", dpi=150)
plt.show()