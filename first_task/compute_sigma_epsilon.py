import csv
from pathlib import Path

import numpy as np


# Parameters
ORDER = 3
G_PERCENT = 33.0
FREQUENCIES_GHZ = [0.5, 0.6, 0.7, 0.9, 1.0, 2.0, 2.5, 3.5]
OUTPUT_CSV = Path("sigma_epsilon_output.csv")


# Coefficients from dp_maps.py (order 3)
EPS_N3 = {
    (0, 0): 3.46, (0, 1): 0.41, (0, 2): -1.7e-2, (0, 3): 6.1e-4,
    (1, 0): -0.34, (1, 1): 0.15, (1, 2): -4.6e-3,
    (2, 0): -0.14, (2, 1): 1.4e-3,
    (3, 0): 1.9e-2,
}
SIG_N3 = {
    (0, 0): -0.39, (0, 1): 0.16, (0, 2): -8.3e-3, (0, 3): 1.1e-4,
    (1, 0): 8.9e-3, (1, 1): -3.6e-2, (1, 2): 1.1e-3,
    (2, 0): 5.8e-2, (2, 1): 1.6e-3,
    (3, 0): -8.5e-3,
}


def compute_dp(f_ghz: np.ndarray, g_percent: float, coeffs: dict[tuple[int, int], float], n: int) -> np.ndarray:
    result = np.zeros_like(f_ghz, dtype=float)
    for i in range(n + 1):
        for j in range(n - i + 1):
            a_ij = coeffs.get((i, j), 0.0)
            result += a_ij * (f_ghz ** i) * (g_percent ** j)
    return result


def fit_exponential(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    ln_y = np.log(y)
    b, ln_a = np.polyfit(x, ln_y, 1)
    a = float(np.exp(ln_a))
    return a, float(b)


def main() -> None:
    freqs = np.array(FREQUENCIES_GHZ, dtype=float)

    eps_vals = compute_dp(freqs, G_PERCENT, EPS_N3, ORDER)
    sig_poly = compute_dp(freqs, G_PERCENT, SIG_N3, ORDER)

    # Fit exponential model to positive sigma values
    mask_pos = sig_poly > 0
    if np.count_nonzero(mask_pos) < 2:
        raise ValueError("Not enough positive sigma values to fit exponential model.")

    a, b = fit_exponential(freqs[mask_pos], sig_poly[mask_pos])
    sig_exp = a * np.exp(b * freqs)

    sig_final = np.where(sig_poly >= 0, sig_poly, sig_exp)
    freq_hz = freqs * 1e9
    epsilon_pp = (sig_final / (2 * np.pi * freq_hz * 8.854e-12)) 

    with OUTPUT_CSV.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "frequency_ghz",
            "epsilon_r",
            "epsilon_pp",
        ])
        for i, f_ghz in enumerate(freqs):
            writer.writerow([
                f_ghz,
                eps_vals[i],
                epsilon_pp[i],
            ])

    print(f"Saved: {OUTPUT_CSV}")
    print(f"Exponential model: sigma = {a:.6g} * exp({b:.6g} * f)")


if __name__ == "__main__":
    main()
