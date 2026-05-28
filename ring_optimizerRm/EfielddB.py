import os
import re
import glob
import numpy as np
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as mpl_colors
from matplotlib.colors import Normalize
from scipy.interpolate import RegularGridInterpolator
from PIL import Image
import io

# =========================================================
# 1. GEOMETRIC CONFIGURATION
# =========================================================
thick = [1.6, 4.0, 1.4, 6.7, 30.0, 13.85, 0.22, 10.0, 0.22, 13.85, 30.0, 6.7, 1.4]
names = ['Substrate', 'Coupling Medium', 'Skin', 'Fat', 'Muscle', 'Bone',
         'CSF', 'Spinal Cord', 'CSF', 'Bone', 'Muscle', 'Fat', 'Skin']

# List and sort e-field files
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
files = sorted(
    glob.glob(os.path.join(script_dir, 'e-field*.h5')),
    key=lambda x: float(re.search(r'\d+\.?\d*', os.path.basename(x)).group())
)
if not files:
    raise FileNotFoundError(f'No e-field*.h5 file found in: {script_dir}')

from parula_cmap import get_parula_cmap
parula_cmap = get_parula_cmap()

def plot_slice(XG, ZG, slice_interp, title, ylabel, xlabel, cbar_label, clim, cmap, output_name, save_png=True):
    fig, ax = plt.subplots(figsize=(11, 8), facecolor='white')
    fig.subplots_adjust(left=0.08, right=0.72, bottom=0.10, top=0.92)

    norm = Normalize(*clim)
    pcm = ax.pcolormesh(XG, ZG, slice_interp,
                cmap=cmap, norm=norm,
                shading='gouraud')

    # --- TISSUE LAYER INTERFACES ---
    current_z = -thick[0] / 2
    for th, name in zip(thick, names):
        z_end = current_z + th
        mid_z = (current_z + z_end) / 2
        is_csf = (name == 'CSF')
        color = 'red' if is_csf else 'white'
        lw = 1.5 if is_csf else 0.8

        ax.axhline(z_end, color=color, linewidth=lw)
        if is_csf:
            ax.axhline(current_z, color='red', linewidth=1.5)

        ax.text(29.5, mid_z, name, fontsize=9, color='red' if is_csf else 'black',
                va='center', fontweight='bold', clip_on=False)
        current_z = z_end

    ax.set_xlim(-28, 28)
    ax.set_ylim(-thick[0] / 2 - 1, sum(thick) - thick[0] / 2 + 1)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_xlabel(xlabel, fontsize=10)

    cbar_ax = fig.add_axes([0.88, 0.10, 0.02, 0.82])
    cb = fig.colorbar(pcm, cax=cbar_ax)
    cb.set_label(cbar_label, fontweight='bold', fontsize=9)

    if save_png:
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        fig.savefig(os.path.join(results_dir, output_name), dpi=150)
    
    # Capture for GIF
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return img

# Pass 1: Maximum value in the Median Y-plane across all frequencies
print('Pass 1: Searching for maximum field value in the slice across all simulations...')
E_max_slice = 0.0
for fname in files:
    with h5py.File(fname, 'r') as f:
        Y = f['/Mesh line y'][:]
        iy = np.argmin(np.abs(Y))
        E = f['/E-Field']
        # We only need to read the slice to be efficient
        Ex = E['x']['re'][:, iy, :] + 1j * E['x']['im'][:, iy, :]
        Ey = E['y']['re'][:, iy, :] + 1j * E['y']['im'][:, iy, :]
        Ez = E['z']['re'][:, iy, :] + 1j * E['z']['im'][:, iy, :]
        mag_slice = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)
        local_max = np.nanmax(mag_slice)
        if local_max > E_max_slice:
            E_max_slice = local_max
print(f'>>> Slice maximum: {E_max_slice:.3e} V/m')

frames_lin = []
frames_db = []

for fname in files:
    print(f' -> Processing: {os.path.basename(fname)}')
    freq_str = re.search(r'\d+\.?\d*', os.path.basename(fname)).group()
    
    with h5py.File(fname, 'r') as f:
        X = f['/Mesh line x'][:]
        Y = f['/Mesh line y'][:]
        Z = f['/Mesh line z'][:]
        E_raw = f['/E-Field']
        iy = np.argmin(np.abs(Y))
        Ex = E_raw['x']['re'][:, iy, :] + 1j * E_raw['x']['im'][:, iy, :]
        Ey = E_raw['y']['re'][:, iy, :] + 1j * E_raw['y']['im'][:, iy, :]
        Ez = E_raw['z']['re'][:, iy, :] + 1j * E_raw['z']['im'][:, iy, :]
        slice_lin = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)

    # Depth calibration: use a fixed reference (index 24 ~ 2.4355 mm) 
    # which corresponds to the antenna position for all frequencies.
    Z_phys = Z - Z[24]

    # Grid for interpolation (Higher resolution for smoother look)
    x_grid = np.linspace(-28, 28, 800)
    z_grid = np.linspace(-thick[0]/2 - 1, sum(thick) - thick[0]/2 + 1, 1000)
    ZG, XG = np.meshgrid(z_grid, x_grid, indexing='ij')
    interp_pts = np.stack([ZG, XG], axis=-1)

    # Interpolation Linear with cubic-like smoothness (using 'linear' but on high-res grid)
    # Note: RegularGridInterpolator only supports 'linear' or 'nearest' in some versions,
    # but we can improve visual smoothness by interpolating in log-space for dB.
    interp_lin = RegularGridInterpolator((Z_phys, X), slice_lin, method='linear', bounds_error=False, fill_value=0)
    slice_interp_lin = interp_lin(interp_pts)
    
    # Plot Linear (Fixed global scale)
    plot_slice(XG, ZG, slice_interp_lin, 
                        f'Electric Field (Linear) at {freq_str} GHz',
                        'Depth (mm)', 'Lateral Position (mm)', '|E| (V/m)',
                        (0, E_max_slice), parula_cmap, 
                        f'efield_lin_{freq_str}GHz.png', save_png=True)
    
    img_lin_gif = plot_slice(XG, ZG, slice_interp_lin, 
                        f'Electric Field (Linear) at {freq_str} GHz',
                        'Depth (mm)', 'Lateral Position (mm)', '|E| (V/m)',
                        (0, E_max_slice), parula_cmap, "", save_png=False)
    frames_lin.append(img_lin_gif)

    # dB Transformation
    eps = 1e-12
    slice_lin_safe = np.maximum(slice_lin, eps)
    slice_db = 20.0 * np.log10(slice_lin_safe)
    # IMPORTANT: Interpolating the dB values directly gives a smoother "blended" look
    interp_db = RegularGridInterpolator((Z_phys, X), slice_db, method='linear', bounds_error=False, fill_value=-120)
    slice_interp_db = interp_db(interp_pts)
    
    # Plot dB (Fixed scale -20 to 50)
    img_db = plot_slice(XG, ZG, slice_interp_db, 
                       f'Electric Field (dB) at {freq_str} GHz',
                       'Depth (mm)', 'Lateral Position (mm)', '|E| (dB V/m)',
                       (-20, 50), parula_cmap, 
                       f'efield_db_{freq_str}GHz.png', save_png=True)
    frames_db.append(img_db)

# Export GIFs to 'gifs' folder
gif_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs")
if frames_lin:
    frames_lin[0].save(os.path.join(gif_dir, 'efield_linear.gif'), save_all=True, append_images=frames_lin[1:], loop=0, duration=1000)
if frames_db:
    frames_db[0].save(os.path.join(gif_dir, 'efield_dB.gif'), save_all=True, append_images=frames_db[1:], loop=0, duration=1000)

print("Processing complete.")
