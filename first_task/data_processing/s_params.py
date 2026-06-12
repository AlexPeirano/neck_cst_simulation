import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


fichier = Path(__file__).resolve().parent / "S11.txt"

sweeps = []
current_label = None
freq_tmp = []
s11_tmp = []

with open(fichier, 'r') as f:
    for ligne in f:
        ligne = ligne.strip()

        if ligne.startswith('#'):
            # 


