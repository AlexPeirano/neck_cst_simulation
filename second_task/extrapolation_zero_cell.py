import numpy as np
import matplotlib.pyplot as plt

def integration(z, a, n, rule):
    # grille de point
    x = np.linspace(0, a, n+1)
    y = np.linspace(0, a, n+1)

    # taille d'une cellule, distance entre deux noeuds
    h = a/n
    zs = z**2

    if rule == 'midpoint':
        # centre de chaque cellule
        xs = (x[:-1]+h/2)
        ys = (y[:-1]+h/2)

        # grille 2D
        xxs, yys = np.meshgrid(xs, ys)

        integrale = np.sum(1.0/np.sqrt(xxs + yys + zs))
    
    else:
        raise ValueError('unsuported method for now')
    
    return integrale * h**2

ns = [5, 7, 10, 15, 20]
hs = np.array([1.0/n for n in ns])

I_mid = np.array([integration(1,1,n,'midpoint') for n in ns])

pfit_mid = np.polyfit(hs**2, I_mid, 2)
I0_mid = pfit_mid[-1]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(hs**2, I_mid, 'o-', color='steelblue')
ax1.axhline(I0_mid, linestyle='--', color='gray',label=f'Extrap = {I0_mid:.6f}')
ax1.set_xlabel('h² [m²]')
ax1.set_ylabel('I_midp [m]')
ax1.legend()

