import matplotlib.pyplot as plt
import skrf as rf
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ------------------------------------------------------------------ #
# Fichiers principaux (répétition des mesures myNeck)                  #
# Ordre : no MM, 5%, 20%                                               #
# ------------------------------------------------------------------ #
SIM_FILES = [
    ("nomm.s2p", "no matching medium"),
    ("5%.s2p",   "5% graphite matching medium"),
    ("20%.s2p",  "20% graphite matching medium"),
]

SAFE_LABELS = {
    "no matching medium":           "noMM",
    "5% graphite matching medium":  "5pct",
    "20% graphite matching medium": "20pct",
}

FOLDER_NAME = "experiments_2"

COLORS = {
    "s11": "#2196F3",
    "s22": "#E91E63",
    "s12": "#FF9800",
    "s21": "#4CAF50",
}


def load_network(path: Path):
    if not path.exists():
        print(f"  [AVERTISSEMENT] Fichier non trouvé : {path}")
        return None
    return rf.Network(str(path))


# ------------------------------------------------------------------ #
# Figure 1 : Sans matching medium → 2 subplots côte à côte           #
# ------------------------------------------------------------------ #
no_mm_entries    = [(f, l) for f, l in SIM_FILES if l == "no matching medium"]
graphite_entries = [(f, l) for f, l in SIM_FILES if l != "no matching medium"]

for filename, label in no_mm_entries:
    net = load_network(BASE_DIR / filename)
    if net is None:
        continue

    freq_ghz = net.f / 1e9
    s11_db = net.s_db[:, 0, 0]
    s22_db = net.s_db[:, 1, 1]
    s12_db = net.s_db[:, 0, 1]
    s21_db = net.s_db[:, 1, 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"{FOLDER_NAME} — {label}", fontsize=15, fontweight="bold")

    # Subplot S11 & S22
    ax1.set_title("S11 & S22", fontsize=13)
    ax1.set_xlabel("Frequency [GHz]", fontsize=11)
    ax1.set_ylabel("Magnitude [dB]", fontsize=11)
    ax1.axhline(y=-10, color="black", linestyle="--", linewidth=1, label="-10 dB")
    ax1.plot(freq_ghz, s11_db, color=COLORS["s11"], linestyle="-",  linewidth=1.8, label="S11")
    ax1.plot(freq_ghz, s22_db, color=COLORS["s22"], linestyle="--", linewidth=1.8, label="S22")
    ax1.legend(fontsize=9, loc="upper right")
    ax1.grid(True, alpha=0.35)

    # Subplot S12 & S21
    ax2.set_title("S12 & S21", fontsize=13)
    ax2.set_xlabel("Frequency [GHz]", fontsize=11)
    ax2.set_ylabel("Magnitude [dB]", fontsize=11)
    ax2.plot(freq_ghz, s12_db, color=COLORS["s12"], linestyle="-",  linewidth=1.8, label="S12")
    ax2.plot(freq_ghz, s21_db, color=COLORS["s21"], linestyle="--", linewidth=1.8, label="S21")
    ax2.legend(fontsize=9, loc="upper right")
    ax2.grid(True, alpha=0.35)

    fig.tight_layout()
    safe = SAFE_LABELS[label]
    out = BASE_DIR / f"{FOLDER_NAME}_{safe}_combined.png"
    fig.savefig(out, dpi=150)
    print(f"  Sauvegardé : {out}")
    plt.close(fig)


# ------------------------------------------------------------------ #
# Figure 2 : Graphite (5% + 20%) → 4 subplots (2 lignes × 2 cols)   #
# ------------------------------------------------------------------ #
nets_graphite = []
for filename, label in graphite_entries:
    net = load_network(BASE_DIR / filename)
    if net is not None:
        nets_graphite.append((net, label))

if len(nets_graphite) >= 1:
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"{FOLDER_NAME} — Graphite matching media comparison", fontsize=15, fontweight="bold")

    for row_idx, (net, label) in enumerate(nets_graphite):
        freq_ghz = net.f / 1e9
        s11_db = net.s_db[:, 0, 0]
        s22_db = net.s_db[:, 1, 1]
        s12_db = net.s_db[:, 0, 1]
        s21_db = net.s_db[:, 1, 0]

        # Colonne 0 : S11 & S22
        ax = axes[row_idx, 0]
        ax.set_title(f"S11 & S22  |  {label}", fontsize=12)
        ax.set_xlabel("Frequency [GHz]", fontsize=10)
        ax.set_ylabel("Magnitude [dB]", fontsize=10)
        ax.axhline(y=-10, color="black", linestyle="--", linewidth=1, label="-10 dB")
        ax.plot(freq_ghz, s11_db, color=COLORS["s11"], linestyle="-",  linewidth=1.8, label="S11")
        ax.plot(freq_ghz, s22_db, color=COLORS["s22"], linestyle="--", linewidth=1.8, label="S22")
        ax.legend(fontsize=9, loc="upper right")
        ax.grid(True, alpha=0.35)

        # Colonne 1 : S12 & S21
        ax = axes[row_idx, 1]
        ax.set_title(f"S12 & S21  |  {label}", fontsize=12)
        ax.set_xlabel("Frequency [GHz]", fontsize=10)
        ax.set_ylabel("Magnitude [dB]", fontsize=10)
        ax.plot(freq_ghz, s12_db, color=COLORS["s12"], linestyle="-",  linewidth=1.8, label="S12")
        ax.plot(freq_ghz, s21_db, color=COLORS["s21"], linestyle="--", linewidth=1.8, label="S21")
        ax.legend(fontsize=9, loc="upper right")
        ax.grid(True, alpha=0.35)

    fig.tight_layout()
    out = BASE_DIR / f"{FOLDER_NAME}_graphite_combined.png"
    fig.savefig(out, dpi=150)
    print(f"  Sauvegardé : {out}")
    plt.close(fig)


# ------------------------------------------------------------------ #
# Figure 3 : twentycm.s2p — Antennes à l'air libre à 20 cm          #
# 4 subplots indépendants : S11, S22, S12, S21                       #
# ------------------------------------------------------------------ #
net_20cm = load_network(BASE_DIR / "twentycm.s2p")

if net_20cm is not None:
    freq_ghz = net_20cm.f / 1e9
    s11_db = net_20cm.s_db[:, 0, 0]
    s22_db = net_20cm.s_db[:, 1, 1]
    s12_db = net_20cm.s_db[:, 0, 1]
    s21_db = net_20cm.s_db[:, 1, 0]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        f"{FOLDER_NAME} — Antennas in free air at 20 cm distance",
        fontsize=15, fontweight="bold"
    )

    # S11
    ax = axes[0, 0]
    ax.set_title("S11", fontsize=13)
    ax.set_xlabel("Frequency [GHz]", fontsize=11)
    ax.set_ylabel("Magnitude [dB]", fontsize=11)
    ax.axhline(y=-10, color="black", linestyle="--", linewidth=1, label="-10 dB")
    ax.plot(freq_ghz, s11_db, color=COLORS["s11"], linestyle="-", linewidth=1.8, label="S11")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.35)

    # S22
    ax = axes[0, 1]
    ax.set_title("S22", fontsize=13)
    ax.set_xlabel("Frequency [GHz]", fontsize=11)
    ax.set_ylabel("Magnitude [dB]", fontsize=11)
    ax.axhline(y=-10, color="black", linestyle="--", linewidth=1, label="-10 dB")
    ax.plot(freq_ghz, s22_db, color=COLORS["s22"], linestyle="--", linewidth=1.8, label="S22")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.35)

    # S12
    ax = axes[1, 0]
    ax.set_title("S12", fontsize=13)
    ax.set_xlabel("Frequency [GHz]", fontsize=11)
    ax.set_ylabel("Magnitude [dB]", fontsize=11)
    ax.plot(freq_ghz, s12_db, color=COLORS["s12"], linestyle="-", linewidth=1.8, label="S12")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.35)

    # S21
    ax = axes[1, 1]
    ax.set_title("S21", fontsize=13)
    ax.set_xlabel("Frequency [GHz]", fontsize=11)
    ax.set_ylabel("Magnitude [dB]", fontsize=11)
    ax.plot(freq_ghz, s21_db, color=COLORS["s21"], linestyle="--", linewidth=1.8, label="S21")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.35)

    fig.tight_layout()
    out = BASE_DIR / f"{FOLDER_NAME}_twentycm_4subplots.png"
    fig.savefig(out, dpi=150)
    print(f"  Sauvegardé : {out}")
    plt.close(fig)

print("\nTous les graphiques ont été générés.")
