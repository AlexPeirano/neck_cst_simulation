import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLUMNS = {"[Hz]", "name", "permittivity", "[S/m]"}


def load_cst_csv(filename):
    """Charge et nettoie les données exportées de CST."""
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")

    # On saute les 2 premières lignes d'en-tête pour lire les colonnes correctement
    df = pd.read_csv(path, skiprows=2)

    # Nettoyage des noms de colonnes
    df.columns = [c.strip() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans {path.name}: {sorted(missing)}. "
            f"Colonnes trouvées: {list(df.columns)}"
        )

    # Conversion des colonnes numériques
    df["[Hz]"] = pd.to_numeric(df["[Hz]"], errors="coerce")
    df["permittivity"] = pd.to_numeric(df["permittivity"], errors="coerce")
    df["[S/m]"] = pd.to_numeric(df["[S/m]"], errors="coerce")

    # Suppression des lignes invalides
    before = len(df)
    df = df.dropna(subset=["[Hz]", "permittivity", "[S/m]", "name"]).copy()
    removed = before - len(df)
    if removed > 0:
        print(f"[INFO] {path.name}: {removed} ligne(s) ignorée(s) (valeurs invalides).")

    # Conversion de la fréquence en GHz
    df["Freq_GHz"] = df["[Hz]"] / 1e9
    return df


def main():
    # Fichiers d'entrée
    file1 = "spinal_cord.csv"
    file2 = "white_matter.csv"

    print("[INFO] Chargement des fichiers...")
    df1 = load_cst_csv(file1)
    df2 = load_cst_csv(file2)

    # 2. Création de la figure
    fig, ax1 = plt.subplots(figsize=(12, 7))
    ax2 = ax1.twinx()  # Création de l'axe de droite

    # --- PLOT MATÉRIAU 1 (Lignes pleines) ---
    name1 = str(df1["name"].iloc[0]).strip()
    ax1.plot(df1["Freq_GHz"], df1["permittivity"], color="blue", label=f"eps_r ({name1})", linewidth=2)
    ax2.plot(df1["Freq_GHz"], df1["[S/m]"], color="red", label=f"sigma ({name1})", linewidth=2)

    # --- PLOT MATÉRIAU 2 (Lignes en pointillés) ---
    name2 = str(df2["name"].iloc[0]).strip()
    ax1.plot(df2["Freq_GHz"], df2["permittivity"], color="green", linestyle="--", label=f"eps_r ({name2})", linewidth=2)
    ax2.plot(df2["Freq_GHz"], df2["[S/m]"], color="orange", linestyle="--", label=f"sigma ({name2})", linewidth=2)

    # 3. Configuration des axes et titres
    ax1.set_xlabel("Frequency [GHz]", fontsize=12)
    ax1.set_ylabel("Relative Permitivity ($\\epsilon_r$)", color="blue", fontsize=12)
    ax2.set_ylabel("Conductivity [S/m]", color="red", fontsize=12)

    plt.title(f"Dielectric Properties Comparaisons : {name1} vs {name2}", fontsize=14)
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)

    # 4. Légende combinée
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True)

    plt.tight_layout()
    print("[INFO] Affichage du graphique...")
    plt.show()
    print("[OK] Terminé.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERREUR] {e}")
        sys.exit(1)