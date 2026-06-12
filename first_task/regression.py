import argparse

import numpy as np


def fit_exponential(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
	"""Fit y = a * exp(b * x) and return (a, b, r_squared)."""
	ln_y = np.log(y)
	b, ln_a = np.polyfit(x, ln_y, 1)
	a = float(np.exp(ln_a))

	y_hat = a * np.exp(b * x)
	ss_res = np.sum((y - y_hat) ** 2)
	ss_tot = np.sum((y - np.mean(y)) ** 2)
	r_squared = 1.0 - (ss_res / ss_tot if ss_tot != 0 else np.nan)

	return a, float(b), float(r_squared)


# Sigma coefficients from dp_maps.py
sig_N2 = {
	(0, 0): 1.23, (0, 1): -0.14, (0, 2): 2.6e-3,
	(1, 0): -0.44, (1, 1): 2.6e-2,
	(2, 0): 3.2e-2,
}
sig_N3 = {
	(0, 0): -0.39, (0, 1): 0.16, (0, 2): -8.3e-3, (0, 3): 1.1e-4,
	(1, 0): 8.9e-3, (1, 1): -3.6e-2, (1, 2): 1.1e-3,
	(2, 0): 5.8e-2, (2, 1): 1.6e-3,
	(3, 0): -8.5e-3,
}
sig_N4 = {
	(0, 0): 6.6e-2, (0, 1): -0.13, (0, 2): 1.5e-2, (0, 3): -5.1e-4, (0, 4): 5.2e-6,
	(1, 0): 1.0e-1, (1, 1): 4.6e-3, (1, 2): -1.6e-3, (1, 3): 3.5e-5,
	(2, 0): -4.2e-2, (2, 1): 6.3e-3, (2, 2): 1.1e-5,
	(3, 0): 9.7e-4, (3, 1): -6.8e-4,
	(4, 0): 7.3e-4,
}


def compute_dp(f: np.ndarray, g: np.ndarray, coeffs: dict[tuple[int, int], float], n: int) -> np.ndarray:
	result = np.zeros_like(f, dtype=float)
	for i in range(n + 1):
		for j in range(n - i + 1):
			a_ij = coeffs.get((i, j), 0.0)
			result += a_ij * (f ** i) * (g ** j)
	return result


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Exponential regression for sigma values from DP formula: y = a * exp(b * x)."
	)
	parser.add_argument("--order", type=int, choices=[2, 3, 4], default=3, help="Polynomial order N")
	parser.add_argument("--x-var", choices=["frequency", "graphite"], default="frequency",
		help="Choose x variable for regression")
	parser.add_argument("--f-min", type=float, default=0.5, help="Min frequency in GHz")
	parser.add_argument("--f-max", type=float, default=3.5, help="Max frequency in GHz")
	parser.add_argument("--f-points", type=int, default=200, help="Number of frequency samples")
	parser.add_argument("--g-min", type=float, default=0.0, help="Min graphite percentage")
	parser.add_argument("--g-max", type=float, default=100.0, help="Max graphite percentage")
	parser.add_argument("--g-points", type=int, default=101, help="Number of graphite samples")
	parser.add_argument("--fixed-g", type=float, default=10.0, help="Graphite value when x-var=frequency")
	parser.add_argument("--fixed-f", type=float, default=1.0, help="Frequency in GHz when x-var=graphite")
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	coeffs_map = {2: sig_N2, 3: sig_N3, 4: sig_N4}
	coeffs = coeffs_map[args.order]

	if args.x_var == "frequency":
		x = np.linspace(args.f_min, args.f_max, args.f_points)
		g = np.full_like(x, args.fixed_g, dtype=float)
		f = x
		x_label = "frequency"
	else:
		x = np.linspace(args.g_min, args.g_max, args.g_points)
		f = np.full_like(x, args.fixed_f, dtype=float)
		g = x
		x_label = "graphite"

	y = compute_dp(f, g, coeffs, args.order)

	mask = np.isfinite(x) & np.isfinite(y) & (y > 0)
	x = x[mask]
	y = y[mask]

	if len(x) < 2:
		raise ValueError("Not enough valid points (need at least 2) after filtering y > 0.")

	a, b, r_squared = fit_exponential(x, y)

	print("Exponential regression model (from DP formula):")
	print(f"  sigma = {a:.6g} * exp({b:.6g} * {x_label})")
	print(f"R^2 score: {r_squared:.6f}")


if __name__ == "__main__":
	main()
