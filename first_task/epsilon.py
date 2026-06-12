import numpy as np
import pandas as pd
from pathlib import Path


def epsilon_prime(epsilon_r, epsilon_zero):
    return epsilon_r * epsilon_zero


def epsilon_prime_prime(conductivity, frequency):
    omega = 2 * np.pi * frequency
    out = np.full_like(omega, np.nan, dtype=float)
    np.divide(conductivity, omega, out=out, where=omega != 0)
    return out


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize header format
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
    )

    # Common aliases -> canonical names
    aliases = {
        "frequency": "frequency",
        "freq": "frequency",
        "frequency_hz": "frequency",
        "f": "frequency",
        "conductivity": "conductivity",
        "sigma": "conductivity",
        "conductivite": "conductivity",
        "epsilon_r": "epsilon_r",
        "eps_r": "epsilon_r",
        "epsilonzero": "epsilon_zero",
        "epsilon_0": "epsilon_zero",
        "epsilon0": "epsilon_zero",
        "eps0": "epsilon_zero",
        "epsilon_zero": "epsilon_zero",
    }

    rename_map = {c: aliases[c] for c in df.columns if c in aliases}
    return df.rename(columns=rename_map)


def detect_header_and_sep(path: Path) -> tuple[int, str]:
    lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    seps = [",", ";", "\t"]
    tokens = ["frequency", "freq", "epsilon", "eps", "conduct", "sigma"]

    best_row = -1
    best_sep = ","
    best_score = -1

    for i, line in enumerate(lines[:80]):
        if not line.strip():
            continue

        low = line.lower()
        token_score = sum(t in low for t in tokens)
        if token_score == 0:
            continue

        sep = max(seps, key=lambda s: line.count(s))
        col_count = line.count(sep) + 1
        if col_count < 2:
            continue

        score = token_score * 10 + col_count
        if score > best_score:
            best_score = score
            best_row = i
            best_sep = sep

    if best_row == -1:
        raise ValueError("Could not detect table header row in CSV.")
    return best_row, best_sep


# Build paths from script location
base_dir = Path(__file__).resolve().parent
input_file = base_dir / "spinal_cord.csv"
output_file = base_dir / "epsilon_output.csv"

if not input_file.exists():
    raise FileNotFoundError(f"Input file not found: {input_file}")

header_row, sep = detect_header_and_sep(input_file)
df = pd.read_csv(
    input_file,
    skiprows=header_row,
    sep=sep,
    engine="python",
    encoding="utf-8-sig",
)

df = normalize_columns(df)

required_cols = {"frequency", "epsilon_r", "epsilon_zero", "conductivity"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)} | Found: {list(df.columns)}")

# Ensure numeric values (supports decimal comma)
for col in required_cols:
    df[col] = pd.to_numeric(
        df[col].astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )

result = pd.DataFrame({
    "Frequency": df["frequency"],
    "epsilon_prime": epsilon_prime(df["epsilon_r"], df["epsilon_zero"]),
    "epsilon_prime_prime": epsilon_prime_prime(df["conductivity"], df["frequency"]),
})

result.to_csv(output_file, index=False)
print(result.head())
print(f"\nSaved: {output_file}")