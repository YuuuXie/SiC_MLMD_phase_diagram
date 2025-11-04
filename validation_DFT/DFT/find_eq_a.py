import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


def find_equilibrium_lattice_constant(filename):
    # Load data
    # The columns are:
    # 0: Pressure(GPa), 1: Enthalpy/Atom(eV), 2: Volume/Atom(Angstrom^3),
    # 3: Energy/Atom(eV), 4: Num_Atoms, 5: Lattice_a(Angstrom)
    data = np.loadtxt(filename, comments='#')

    # Extract columns: lattice a (last column) and Energy/Atom (4th column)
    lattice_a = data[:, 5]
    energy = data[:, 3]

    # Sort
    sort_idx = np.argsort(lattice_a)
    lattice_a_sorted = lattice_a[sort_idx]
    energy_sorted = energy[sort_idx]

    # Fit a cubic spline to the Energy vs. Lattice_a data
    cs = CubicSpline(lattice_a_sorted, energy_sorted)

    # Make a fine grid of lattice constants over the range of the data
    a_fine = np.linspace(lattice_a_sorted.min(), lattice_a_sorted.max(), 1000)
    energy_fine = cs(a_fine)

    # Find the lattice constant corresponding to the minimal interpolated energy
    idx_min = np.argmin(energy_fine)
    a_min = a_fine[idx_min]
    energy_min = energy_fine[idx_min]

    print(f"Equilibrium lattice constant: {a_min:.6f} Angstrom")
    print(f"Minimum Energy/Atom: {energy_min:.6f} eV")

    # plot data and the fit
    plt.figure(figsize=(8,6))
    plt.plot(lattice_a_sorted, energy_sorted, 'o', label="Data")
    plt.plot(a_fine, energy_fine, '-', label="Cubic Spline")
    plt.plot(a_min, energy_min, 'rx', markersize=10, label="Minimum")
    plt.xlabel("Lattice a (Angstrom)")
    plt.ylabel("Energy/Atom (eV)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"equilibrium_lattice_{filename}.png")


if __name__ == "__main__":
    find_equilibrium_lattice_constant("rs_enthalpy_dft.txt")
    find_equilibrium_lattice_constant("zb_enthalpy_dft.txt")