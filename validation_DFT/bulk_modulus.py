import numpy as np
import matplotlib.pyplot as plt
from eos import fit_to_eos, get_eos
from ase.units import GPa

def get_bulk_modulus(filename, eos="birch_murnaghan"):
    """Calculate bulk modulus by fitting eos to energy-volume data."""
    # Get the initial volume and energy
    data = np.loadtxt(filename, comments="#")
    volume = data[:, 2]
    energy = data[:, 3]

    # Fit the EOS
    e, bulk_modulus, bp, ev = fit_to_eos(volume, energy, get_eos(eos))

    # convert to GPa

    return bulk_modulus / GPa

def plot_eos_fit(filename, eos="vinet", savefig=None):
    """
    Load energy–volume data from file, fit an EOS, and plot the data with the fit.
    
    Parameters:
      filename (str): Path to the data file. The file is assumed to have columns:
                      [0] Pressure, [1] Enthalpy, [2] Volume/Atom, [3] Energy/Atom, 
                      [4] Num_Atoms, [5] Lattice_a
      eos (str): EOS model identifier (e.g. "vinet" or "birch_murnaghan")
      savefig (str): Filename for the PNG image. If None, will replace .txt with .png
      
    Returns:
      e, bulk_modulus, bp, ev : fitted EOS parameters.
    """
    data = np.loadtxt(filename, comments="#")
    volume = data[:, 2]
    energy = data[:, 3]
    
    # Fit Vinet EOS
    eos_vinet = get_eos("vinet")
    e0_v, bulk_v, bp_v, v0_v = fit_to_eos(volume, energy, eos_vinet)
    # Fit Birch–Murnaghan EOS
    eos_birch = get_eos("birch_murnaghan")
    e0_b, bulk_b, bp_b, v0_b = fit_to_eos(volume, energy, eos_birch)
    
    # Create a fine grid for volume
    v_plot = np.linspace(volume.min(), volume.max(), 200)
    energy_fit_v = eos_vinet(v_plot, e0_v, bulk_v, bp_v, v0_v)
    energy_fit_b = eos_birch(v_plot, e0_b, bulk_b, bp_b, v0_b)
    
    # Plot the data and the fits
    plt.figure(figsize=(8,6))
    plt.scatter(volume, energy, color="black", marker="o", label="Data")
    plt.plot(v_plot, energy_fit_v, "r-", lw=2, label="Vinet EOS fit")
    plt.plot(v_plot, energy_fit_b, "b--", lw=2, label="Birch-Murnaghan EOS fit")
    plt.xlabel("Volume/Atom (Å³)")
    plt.ylabel("Energy/Atom (eV)")
    plt.legend()
    
    if savefig is None:
        savefig = filename.replace(".txt", ".png")
    plt.savefig(savefig, dpi=300)
    plt.close()
    
    vinet_params = (e0_v, bulk_v / GPa, bp_v, v0_v)
    birch_params = (e0_b, bulk_b / GPa, bp_b, v0_b)
    return vinet_params, birch_params

# Example usage:
if __name__ == "__main__":
    # List of files to process
    files = [f"rs_near_equilibrium_0.98_1.02_40.txt",
             f"DFT/rs_near_equilibrium_0.98_1.02_40_enthalpy_dft.txt",
             f"zb_near_equilibrium_0.98_1.02_40.txt",
            f"DFT/zb_near_equilibrium_0.98_1.02_40_enthalpy_dft.txt",
             ]
    
    for f in files:
        # Create and save the plot.
        vinet_params, birch_params = plot_eos_fit(f)
        print(f"Bulk modulus for {f} (Vinet): {vinet_params[1]:.2f} GPa")
        print(f"Bulk modulus for {f} (Birch): {birch_params[1]:.2f} GPa")
        print(f"Plot saved for {f}")