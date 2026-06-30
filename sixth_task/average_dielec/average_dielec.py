import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Weights for each tissue in the neck model 
weights = {
    'skin':        0.024464831804281342,
    'fat':         0.11708169506334644,
    'muscle':      0.5242463958060288,
    'bone':        0.12101354303189164,
    'csf':         0.03844473569244212,
    'spinal cord': 0.17474879860200962,
}

TISSUE_FILES = {
    'skin':        'skindielec.txt',
    'fat':         'fatdielec.txt',
    'muscle':      'muscledielec.txt',
    'bone':        'bonedielec.txt',
    'csf':         'csfdielec.txt',
    'spinal cord': 'spinalCordDielec.txt',
}

# Frequency bandwidth of interest
F_MIN_GHz = 0.5   # GHz
F_MAX_GHz = 14.0  # GHz


def parse_tissue_file(filepath: str) -> pd.DataFrame:
    """
    Parse a tissue dielectric file with columns:
        tissue_name  frequency[Hz]  conductivity[S/m]  relative_permittivity
    Returns a DataFrame with columns: freq_GHz, sigma, epsilon_r
    """
    rows = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            # Data lines have exactly 4 fields; the first is the tissue name (no spaces)
            if len(parts) != 4:
                continue
            try:
                freq_hz   = float(parts[1])
                sigma     = float(parts[2])
                epsilon_r = float(parts[3])
                rows.append({
                    'freq_GHz': freq_hz / 1e9,
                    'sigma':    sigma,
                    'epsilon_r': epsilon_r,
                })
            except ValueError:
                continue  # skip header / separator lines

    df = pd.DataFrame(rows)
    return df


def compute_weighted_average(weights: dict, script_dir: str) -> pd.DataFrame:
    """
    Compute the weighted average of epsilon_r and sigma over all tissues,
    restricted to the bandwidth [F_MIN_GHz, F_MAX_GHz].

    Returns a DataFrame with columns:
        freq_GHz, epsilon_r_avg, sigma_avg
    """
    total_weight = sum(weights.values())
    tissue_dfs = {}
    for tissue, filename in TISSUE_FILES.items():
        filepath = os.path.join(script_dir, filename)
        df = parse_tissue_file(filepath)
        # Filter to bandwidth
        df = df[(df['freq_GHz'] >= F_MIN_GHz) & (df['freq_GHz'] <= F_MAX_GHz)].reset_index(drop=True)
        tissue_dfs[tissue] = df

    # Use the frequency grid from the first tissue (all files share the same grid)
    ref_tissue = list(tissue_dfs.keys())[0]
    freq_GHz = tissue_dfs[ref_tissue]['freq_GHz'].values

    epsilon_avg = np.zeros(len(freq_GHz))
    sigma_avg   = np.zeros(len(freq_GHz))

    for tissue, w in weights.items():
        df = tissue_dfs[tissue]
        # Interpolate to reference frequency grid to be safe
        eps_interp   = np.interp(freq_GHz, df['freq_GHz'].values, df['epsilon_r'].values)
        sigma_interp = np.interp(freq_GHz, df['freq_GHz'].values, df['sigma'].values)
        epsilon_avg += w * eps_interp
        sigma_avg   += w * sigma_interp

    result = pd.DataFrame({
        'freq_GHz':  freq_GHz,
        'epsilon_r': epsilon_avg,
        'sigma_S_m': sigma_avg,
    })
    return result


def plot_and_save(df: pd.DataFrame, output_dir: str):
    """
    Plot epsilon_r and sigma vs frequency on the same figure (dual y-axis)
    and save a CSV of the results.
    """
    freq = df['freq_GHz'].values
    eps  = df['epsilon_r'].values
    sig  = df['sigma_S_m'].values

    # ── Save CSV ──────────────────────────────────────────────────────────────
    csv_path = os.path.join(output_dir, 'average_dielectric.csv')
    df.to_csv(csv_path, index=False, float_format='%.6e',
              columns=['freq_GHz', 'epsilon_r', 'sigma_S_m'])

    color_eps = '#e94560'   # vivid red  -> epsilon_r
    color_sig = '#4cc9f0'   # cyan       -> sigma

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Epsilon (left axis)
    lns1 = ax1.plot(freq, eps, color='red', linewidth=2.0,
                    label=r'$\varepsilon_r$ (relative permittivity)')
    ax1.set_xlabel('Frequency (GHz)', fontsize=12)
    ax1.set_ylabel(r'Relative permittivity $\varepsilon_r$', color='red', fontsize=12)
    ax1.tick_params(axis='x', colors='black')
    ax1.tick_params(axis='y', colors='red')
    ax1.set_xlim(F_MIN_GHz, F_MAX_GHz)
    ax1.set_xticks([0.5, 2, 4, 6, 8, 10, 12, 14])
    ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax1.grid(which='major', linestyle='--', linewidth=0.5, color='#444', alpha=0.7)
    ax1.grid(which='minor', linestyle=':', linewidth=0.3, color='#333', alpha=0.5)

    # Sigma (right axis)
    ax2 = ax1.twinx()
    lns2 = ax2.plot(freq, sig, color='purple', linewidth=2.0,
                    label=r'$\sigma$ (conductivity)')
    ax2.set_ylabel(r'Conductivity $\sigma$ (S/m)', color='purple', fontsize=12)
    ax2.tick_params(axis='y', colors='purple')
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    # Combined legend
    lns = lns1 + lns2
    labs = [ln.get_label() for ln in lns]
    legend = ax1.legend(lns, labs, loc='upper right', framealpha=0.2,
                        facecolor='#0f3460', edgecolor='#888', fontsize=10)
    legend_colors = ['red', 'purple']
    for text, color in zip(legend.get_texts(), legend_colors):
        text.set_color(color)

    plt.title(
        'Weighted-average dielectric properties of neck tissues\n'
        f'({F_MIN_GHz}–{F_MAX_GHz} GHz)', fontsize=13, pad=12
    )

    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'average_dielectric.png')
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor())
    print(f"Plot saved -> {plot_path}")
    plt.show()


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df_avg = compute_weighted_average(weights, script_dir)
    plot_and_save(df_avg, script_dir)
