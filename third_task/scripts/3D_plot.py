import glob
import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np
from scipy.interpolate import griddata

def plot_cst_data_on_structure(data_file):
    # 1. Configuration des dimensions (épaisseur en mm)
    half_sequence = [
        ("Substrate", 1.6, "#808080", 24), # Nom, épaisseur, couleur, largeur_specifique
        ("Coupling", 4.0, "#ADD8E6", 27.4),
        ("Skin", 1.4, "#FFE4C4", 60),
        ("Fat", 6.7, "#FFFFE0", 60),
        ("Muscle", 30.0, "#F08080", 60),
        ("Bone", 13.85, "#FFFFFF", 60),
        ("CSF", 0.22, "#00FFFF", 60),
    ]
    central_layer = ("Spinal Cord", 10.0, "#D8BFD8", 60)
    
    # Construction de la structure complète (Miroir)
    full_layers = half_sequence + [central_layer] + half_sequence[::-1]
    total_height = 60 # Hauteur de référence pour les tissus
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 2. Dessin de la structure géométrique
    current_x = 0
    for name, thick, color, h in full_layers:
        # On centre verticalement si la largeur (h) est < 60
        y_offset = -h / 2
        rect = patches.Rectangle((current_x, y_offset), thick, h, 
                                 edgecolor='black', facecolor=color, alpha=0.3, label=name)
        ax.add_patch(rect)
        current_x += thick

    # 3. Chargement et Visualisation des données CST
    try:
        # Lecture du fichier (en sautant les lignes d'en-tête de CST)
        # On suppose que le séparateur est l'espace
        df = pd.read_csv(data_file, sep=r'\s+', skiprows=2, 
                         names=['x', 'y', 'z', 'Px', 'Py', 'Pz', 'Area'])
        
        # Calcul de la norme du vecteur Powerflow : |P| = sqrt(Px^2 + Py^2 + Pz^2)
        df['P_norm'] = np.sqrt(df['Px']**2 + df['Py']**2 + df['Pz']**2)
        df['P_db'] = 10 * np.log10(df['P_norm'] + 1e-12)
        
        # Interpolation sur une grille reguliere
        x_min, x_max = df['x'].min(), df['x'].max()
        y_min, y_max = df['y'].min(), df['y'].max()
        xi = np.linspace(x_min, x_max, 600)
        yi = np.linspace(y_min, y_max, 300)
        Xi, Yi = np.meshgrid(xi, yi)
        Zi = griddata(
            (df['x'].values, df['y'].values),
            df['P_db'].values,
            (Xi, Yi),
            method='linear'
        )

        Zi_masked = np.ma.masked_invalid(Zi)
        sc = ax.imshow(
            Zi_masked,
            extent=[x_min, x_max, y_min, y_max],
            origin='lower',
            cmap='turbo',
            vmin=-10,
            vmax=50,
            alpha=0.9,
            interpolation='nearest'
        )
        
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Puissance (dB V.A/m^2)')
        
    except Exception as e:
        print(f"Erreur lors de la lecture des données : {e}")

    # 4. Finalisation du graphique
    ax.set_xlim(0, current_x)
    ax.set_ylim(-35, 35)
    ax.set_aspect('equal')
    file_label = os.path.splitext(os.path.basename(data_file))[0]
    ax.set_title(f"Visualisation du Flux de Puissance sur le Modèle Multicouche\n{file_label}")
    ax.set_xlabel("Profondeur (mm)")
    ax.set_ylabel("Largeur (mm)")
    
    # Suppression des doublons dans la légende
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='small')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "powerflow1")
    files = sorted(glob.glob(os.path.join(data_dir, "powerflow_*.txt")))

    if not files:
        print("Aucun fichier powerflow_*.txt trouve dans powerflow1")
    else:
        for data_file in files:
            plot_cst_data_on_structure(data_file)