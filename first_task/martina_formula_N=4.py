import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# dict containing the relative permitivity coefficients
eps_coeffs = {
    (0,0): 3.89,
    (0,1): -0.25,
    (0,2): 7.7e-2,
    (0,3): -3.1e-3,
    (0,4): 4.2e-5,
    (1,0): -3.9e-1,
    (1,1): -5.4e-2,
    (1,2): 9.2e-3,
    (1,3): -1.9e-4,
    (2,0):  0.14,
    (2,1): -2.2e-2,
    (2,2): 1.7e-4,
    (3,0): 3.5e-3,
    (3,1): 1.6e-3,
    (4,0): 3.5e-3
}

# dict containing the conductivity coefficients
sigma_coeffs = {
    (0,0): 6.6e-2,
    (0,1): -0.13,
    (0,2): 1.5e-2,
    (0,3): -5.1e-4,
    (0,4):  5.2e-6,
    (1,0): 1.0e-1,
    (1,1):  4.6e-3,
    (1,2): -1.6e-3,
    (1,3):  3.5e-5,
    (2,0):  -4.2e-2,
    (2,1):  6.3e-3,
    (2,2):  1.1e-5,
    (3,0):  9.7e-4,
    (3,1): -6.8e-4,
    (4,0):  7.3e-4
}

# grid points computing

## liste of 500 values of frequencies between 1 and 3.5GHz 
freq_liste = np.linspace(1, 3.5, num=500)

## liste of 500 values of graphite between 0 and 50%
graphite_liste = np.linspace(0, 50, 500)

## create a grid 
freq_grid, graphite_grid = np.meshgrid(freq_liste, graphite_liste)

## compute the function for every point of the grid
def martina_formula(F, G, coeffs):
    N = 4
    result = np.zeros_like(F)

    for i in range(N+1):
        for j in range(N-i+1):
            a = coeffs.get((i,j), 0.0)
            result += a * (F**i) * (G**j)

    return result 

# function call

grille_eps = martina_formula(freq_grid, graphite_grid, eps_coeffs)
grille_sig = martina_formula(freq_grid, graphite_grid, sigma_coeffs)

# Create the double plot
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

ax1 = axes[0]
ax2 = axes[1]

fig.suptitle("Martina's Formula N = 4", fontsize=14, fontweight="bold")

# colourmap 
colour_map_eps = ax1.contourf(freq_grid, graphite_grid, grille_eps, levels=100, cmap="magma")

## colour bar
plt.colorbar(colour_map_eps, ax=ax1, label="epsilon_r")

# for sigma < 0: put them at NaN then in black 
sigma_pos = np.where(grille_sig<0, np.nan, grille_sig)

# we put vmin at 0
colour_map_sig = ax2.contourf(freq_grid, graphite_grid, sigma_pos, levels=100, cmap="plasma", vmin=0)
plt.colorbar(colour_map_sig, ax=ax2, label="sigma [S/m]")

# masque for the negative values = 1 else nan, only values in [0.5, 1.5] are the ones from the negative values
negative_masque = np.where(grille_sig<0, 1.0, np.nan)
ax2.contourf(freq_grid, graphite_grid, negative_masque, levels=[0.5, 1.5], colors=["black"])

# Highlight of the zone in interest (between 0 and 0.2)
interest_zone = np.where(grille_sig<0, np.nan, grille_sig)

interest_zone = np.where(grille_sig>0.2, np.nan, grille_sig)

ax2.contourf(freq_grid, graphite_grid, interest_zone, levels=[0.0, 0.2], colors=["cyan"], alpha=0.4)

# contour lines
## epsilon target
eps_threshold = ax1.contour(freq_grid, graphite_grid, grille_eps, levels=[20.0],
                              colors=["red"], linewidths=2.5, linestyles="--")

# label
ax1.clabel(eps_threshold, fmt="epsilon_r = 20", fontsize=9, colors="red")

## sigma line @ 0.2
sig_threshold_1 = ax2.contour(freq_grid, graphite_grid, grille_sig,
                              levels=[0.2], colors=["#13C3F8C9"], linewidths=2.5, linestyles="--")

ax2.clabel(sig_threshold_1, fmt="sigma = 0.2", fontsize=9, colors="#13C3F8C9")

## sigma line @ 0.0
sig_threshold_2 = ax2.contour(freq_grid, graphite_grid, grille_sig,
                               levels=[0.0], colors=["white"], linewidths=2.5, linestyles="-")

ax2.clabel(sig_threshold_2, fmt="sigma = 0.0", fontsize=9, colors="white")

ax1.set_title("Relative permitivity epsilon_r", fontsize=12, fontweight="bold")
ax1.set_xlabel("Frequency [GHz]")
ax1.set_ylabel("Graphite [%]")
ax1.set_xlim(1, 3.5)
ax1.set_ylim(0, 50)

ax2.set_title("Conductivity sigma [S/m]", fontsize=12, fontweight="bold")
ax2.set_xlabel("Frequency [GHz]")
ax2.set_ylabel("Graphite [%]")
ax2.set_xlim(1, 3.5)
ax2.set_ylim(0, 50)

plt.tight_layout()
plt.savefig("heat_map_of_martina_formula_N=4.png", dpi=180, bbox_inches="tight")
plt.close()