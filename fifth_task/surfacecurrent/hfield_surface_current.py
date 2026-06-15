import os
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.interpolate import griddata
from PIL import Image
import io

from parula_cmap import get_parula_cmap

# Map frequency label -> HDF5 file path
FILES = {
    '1.86': 'h-field (f=1.86) [1].h5',
    '2.17': 'h-field (f=2.17) [1].h5',
    '2.69': 'h-field (f=2.69) [1].h5',
}

# Grid resolution for interpolation
GRID_NX = 600
GRID_NY = 800

# GIF frame duration in milliseconds
GIF_DURATION_MS = 1200

OUTPUT_DIR = 'results'

# dB color limits [dB_min, dB_max] 
DB_CLIM = [-40, 0]        # relative dB

PARULA = get_parula_cmap()


def load_hfield(filepath: str):
    """
    Load position and H-field magnitude from a CST HDF5 export.

    Returns
    -------
    x, y : ndarray  — surface point coordinates in mm
    Hmag  : ndarray  — |H| magnitude in A/m
    """
    with h5py.File(filepath, 'r') as f:
        pos    = f['Position'][:]
        hfield = f['H-Field'][:]

    Hx = hfield['x']['re'] + 1j * hfield['x']['im']
    Hy = hfield['y']['re'] + 1j * hfield['y']['im']
    Hz = hfield['z']['re'] + 1j * hfield['z']['im']
    Hmag = np.sqrt(np.abs(Hx)**2 + np.abs(Hy)**2 + np.abs(Hz)**2)

    return pos['x'], pos['y'], Hmag


def interpolate_to_grid(x, y, values, nx=GRID_NX, ny=GRID_NY):
    """
    Scatter-to-grid interpolation using linear griddata.

    Returns
    -------
    XI, YI : 2-D coordinate grids
    Vgrid  : interpolated value grid (NaN outside convex hull)
    """
    xi = np.linspace(x.min(), x.max(), nx)
    yi = np.linspace(y.min(), y.max(), ny)
    XI, YI = np.meshgrid(xi, yi)
    Vgrid = griddata((x, y), values, (XI, YI), method='linear')
    return XI, YI, Vgrid


def _apply_dark_style(ax, cbar_ax):
    """Apply consistent dark background style to axes and colorbar."""
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#444444')
    cbar_ax.yaxis.label.set_color('white')
    cbar_ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar_ax.yaxis.get_ticklabels(), color='white')


def plot_frame(XI, YI, Vgrid, freq_str, clim, cbar_label, title_suffix):
    """
    Render a single frame and return it as a PIL Image.

    Parameters
    ----------
    XI, YI      : meshgrid arrays
    Vgrid       : 2-D data array (same shape as XI/YI)
    freq_str    : frequency label, e.g. '1.86'
    clim        : (vmin, vmax) for the colormap
    cbar_label  : colorbar axis label string
    title_suffix: appended to the title after the frequency, e.g. 'Linear' or 'dB'

    Returns
    -------
    PIL.Image
    """
    fig, ax = plt.subplots(figsize=(7, 9), facecolor='#111111')
    fig.subplots_adjust(left=0.10, right=0.82, bottom=0.07, top=0.93)

    norm = Normalize(*clim)
    x_extent = [XI.min(), XI.max()]
    y_extent = [YI.min(), YI.max()]

    im = ax.imshow(
        Vgrid,
        extent=[*x_extent, *y_extent],
        origin='lower',
        aspect='equal',
        cmap=PARULA,
        norm=norm,
        interpolation='bicubic',
    )

    ax.set_title(
        f'Surface Current ({title_suffix}) — {freq_str} GHz',
        fontsize=13, fontweight='bold', color='white', pad=10,
    )
    ax.set_xlabel('X (mm)', fontsize=10, color='white')
    ax.set_ylabel('Y (mm)', fontsize=10, color='white')

    cbar_ax = fig.add_axes([0.85, 0.07, 0.03, 0.86])
    cb = fig.colorbar(im, cax=cbar_ax)
    cb.set_label(cbar_label, fontweight='bold', fontsize=10)

    _apply_dark_style(ax, cbar_ax)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, facecolor='#111111')
    buf.seek(0)
    img = Image.open(buf).copy()
    plt.close(fig)
    return img


def plot_frame_linear(XI, YI, Hmag_grid, freq_str, global_max):
    """
    Frame showing |H| in linear scale (A/m), normalized to global_max.
    """
    return plot_frame(
        XI, YI, Hmag_grid,
        freq_str=freq_str,
        clim=(0, global_max),
        cbar_label='|H| (A/m)',
        title_suffix='|H| Linear',
    )


def plot_frame_db(XI, YI, Hmag_grid, freq_str, global_max, db_clim=DB_CLIM):
    """
    Frame showing |H| in dB relative to global_max (0 dB = global_max).

    Parameters
    ----------
    db_clim : (dB_min, dB_max) e.g. (-40, 0)
    """
    eps = 1e-30                          # avoid log10(0)
    Hdb = 20.0 * np.log10(np.maximum(Hmag_grid, eps) / global_max)

    return plot_frame(
        XI, YI, Hdb,
        freq_str=freq_str,
        clim=db_clim,
        cbar_label='|H| (dB, rel. to max)',
        title_suffix='|H| dB',
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(script_dir, OUTPUT_DIR), exist_ok=True)

    # Resolve absolute paths
    file_paths = {
        freq: os.path.join(script_dir, rel)
        for freq, rel in FILES.items()
    }

    # --- Pass 1: global maximum for consistent color scale -----------------
    print('Computing global maximum …')
    global_max = 0.0
    for freq, fpath in file_paths.items():
        _, _, Hmag = load_hfield(fpath)
        local_max = float(np.nanmax(Hmag))
        print(f'  f={freq} GHz  max={local_max:.4f} A/m')
        global_max = max(global_max, local_max)
    print(f'  → Global max: {global_max:.4f} A/m\n')

    # --- Pass 2: build frames -----------------------------------------------
    frames_lin = []
    frames_db  = []

    for freq, fpath in file_paths.items():
        print(f'Processing {freq} GHz …')
        x, y, Hmag = load_hfield(fpath)
        XI, YI, Hgrid = interpolate_to_grid(x, y, Hmag)

        frames_lin.append(plot_frame_linear(XI, YI, Hgrid, freq, global_max))
        frames_db.append(plot_frame_db(XI, YI, Hgrid, freq, global_max))
        print(f'  Done.')

    # --- Save GIFs ----------------------------------------------------------
    def save_gif(frames, name):
        path = os.path.join(script_dir, OUTPUT_DIR, name)
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:] + [frames[-1]],   # hold last frame
            loop=0,
            duration=GIF_DURATION_MS,
        )
        print(f'Saved: {path}')

    print('\nSaving GIFs …')
    save_gif(frames_lin, 'hfield_linear.gif')
    save_gif(frames_db,  'hfield_dB.gif')
    print('Done.')


if __name__ == '__main__':
    main()
