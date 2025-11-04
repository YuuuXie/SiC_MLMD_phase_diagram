import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def prepare_spline_data(data):
    # Sort by the first column (pressure)
    sorted_idx = np.argsort(data[:,0])
    data_sorted = data[sorted_idx]
    # Remove duplicate pressures (keep the first occurrence)
    _, unique_idx = np.unique(data_sorted[:,0], return_index=True)
    data_unique = data_sorted[unique_idx]
    return data_unique

def get_energy_shift_at_minimum_no_fit(dft_data, flare_data, tol=1e-6):
    """
    Use DFT data as ground truth. Find the minimum energy from DFT data (column 3)
    along with its lattice constant (column 6). Then find the FLARE energy at the lattice
    constant closest to that DFT equilibrium value and compute the energy shift.
    
    Parameters:
      dft_data (ndarray): DFT data array with columns:
                          [0] Pressure, [1] Enthalpy, [2] Volume,
                          [3] Energy, [4] Num_Atoms, [5] Lattice_a.
      flare_data (ndarray): FLARE data array with the same column structure.
      tol (float): Tolerance for comparing lattice constants.
    
    Returns:
      a_min (float): Equilibrium lattice constant from DFT.
      shift (float): Energy difference (DFT energy – FLARE energy) at a_min.
    """
    # Get DFT minimum energy point.
    dft_min_idx = np.argmin(dft_data[:, 3])
    a_min = dft_data[dft_min_idx, 5]
    dft_min_energy = dft_data[dft_min_idx, 3]
    
    # In FLARE data, find the row with lattice constant closest to a_min.
    flare_idx = np.argmin(np.abs(flare_data[:, 5] - a_min))
    flare_lattice = flare_data[flare_idx, 5]
    flare_energy = flare_data[flare_idx, 3]
    
    # Check if lattice constants match within tolerance.
    if abs(a_min - flare_lattice) > tol:
        print(f"Lattice constant mismatch: DFT a = {a_min:.6f}, FLARE a = {flare_lattice:.6f}, do FLARE calculation.")
        # Here you need to run FLARE calculation at equilibrium lattice
        # using flare_enthalpy.py
    # Compute energy shift as DFT energy minus FLARE energy.
    shift = dft_min_energy - flare_energy

    V_eq = flare_data[flare_idx, 2]
    
    return V_eq, shift


if __name__ == "__main__":

    # Load data
    # DFT data array with columns:
    # [0] Pressure, [1] Enthalpy, [2] Volume, [3] Energy, [4] Num_Atoms, [5] Lattice_a.
    rs = np.loadtxt("rs_enthalpy.txt", comments="#")
    zb = np.loadtxt("zb_enthalpy.txt", comments="#")
    rs_dft = np.loadtxt("DFT/rs_enthalpy_dft.txt", comments="#")
    zb_dft = np.loadtxt("DFT/zb_enthalpy_dft.txt", comments="#")

    # Sort by pressure
    rs = rs[np.argsort(rs[:,0])]
    zb = zb[np.argsort(zb[:,0])]
    rs_dft = rs_dft[np.argsort(rs_dft[:,0])]
    zb_dft = zb_dft[np.argsort(zb_dft[:,0])]

    # Align FLARE electronic energies U to DFT at e-v equilibrium
    V0_rs, shift_rs = get_energy_shift_at_minimum_no_fit(rs_dft, rs)
    V0_zb, shift_zb = get_energy_shift_at_minimum_no_fit(zb_dft, zb)
    mean_shift = (shift_rs + shift_zb) / 2
    # Apply mean shift to enthalpy (H = U + PV) and electronic energy U
    for i in [1, 3]:
        rs[:, i] += mean_shift
        zb[:, i] += mean_shift
        # rs[:, i] += shift_rs
        # zb[:, i] += shift_zb

    # Filter data to pressures below GPa
    P_lim = [-20, 220]
    mask_zb = (zb_dft[:, 0] < P_lim[1]) & (zb_dft[:, 0] > P_lim[0])
    mask_rs = (rs_dft[:, 0] < P_lim[1]) & (rs[:, 0] > P_lim[0])

    # H-p
    p_rs   = rs[mask_rs, 0] 
    H_rs   = rs[mask_rs, 1]
    p_rs_dft = rs_dft[mask_rs, 0]
    H_rs_dft = rs_dft[mask_rs, 1]
    H_zb   = zb[mask_zb, 1]
    p_zb   = zb[mask_zb, 0]
    p_zb_dft = zb_dft[mask_zb, 0]
    H_zb_dft = zb_dft[mask_zb, 1]

    # U-V
    V_rs = rs[mask_rs, 2]
    U_rs = rs[mask_rs, 3]
    V_rs_dft = rs_dft[mask_rs, 2]
    U_rs_dft = rs_dft[mask_rs, 3]
    V_zb = zb[mask_zb, 2]
    U_zb = zb[mask_zb, 3]
    V_zb_dft = zb_dft[mask_zb, 2]
    U_zb_dft = zb_dft[mask_zb, 3]

    plt.rcParams.update({
        "font.size": 14})

    # Plot enthalpy vs pressure
    # Prepare DFT data for cubic spline
    rs_dft_clean = prepare_spline_data(rs_dft)
    zb_dft_clean = prepare_spline_data(zb_dft)

    rs_dft_spline = CubicSpline(rs_dft_clean[:,0], rs_dft_clean[:,1])
    zb_dft_spline = CubicSpline(zb_dft_clean[:,0], zb_dft_clean[:,1])

    rs_dft_interp = rs_dft_spline(p_rs)
    zb_dft_interp = zb_dft_spline(p_zb)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8,10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    ax1.plot(p_rs, H_rs, 'o-', label="Rock Salt FLARE")
    ax1.plot(p_zb, H_zb, 's-', label="Zinc Blende FLARE")
    ax1.plot(p_rs_dft, H_rs_dft, '^-', label="Rock Salt DFT")
    ax1.plot(p_zb_dft, H_zb_dft, 'v-', label="Zinc Blende DFT")
    ax1.set_ylabel("Enthalpy (eV/atom)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Enthalpy vs Pressure for SiC Phases")

    # Residuals (interpolated DFT - FLARE)
    rs_resid = (rs_dft_interp - H_rs)*1e3
    zb_resid = (zb_dft_interp - H_zb)*1e3

    ax2.plot(p_rs, rs_resid, 'o-', label="Rock Salt (DFT - FLARE)")
    ax2.plot(p_zb, zb_resid, 's-', label="Zinc Blende (DFT - FLARE)")
    ax2.axhline(0, color='grey', linestyle='--', linewidth=1)
    ax2.set_xlabel("Pressure (GPa)")
    ax2.set_ylabel("Difference (meV/atom)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("enthalpy_with_residual.png", dpi=300)
    plt.close()
