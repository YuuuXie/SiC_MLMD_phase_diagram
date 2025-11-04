"""Calculate enthalpy vs pressure using FLARE potential in LAMMPS.
1. Setup your LAMMPS (paired with FLARE) executable path in the code below.
2. Please download the uncertainty files: L_inv_lmp.flare, sparse_desc_lmp.flare from
https://doi.org/10.5281/zenodo.14648292 'Test_Unc.zip' before running.
3. GPU node is recommended for faster calculation.
4. Load relevant modules on your HPC system if necessary.
module load intel-mkl/23.0.0-fasrc01 gcc/12.2.0-fasrc01 openmpi/4.1.4-fasrc01 cuda/12.4.1-fasrc01 
"""
import os, shutil
import numpy as np
from ase.io import read
from ase.build import bulk
from ase import units
from flare.md.lammps import get_flare_lammps_calc
# from flare.md.lammps import LAMMPS_MOD

import pdb

# !!! Please set the LAMMPS executable path here
os.environ["lmp"] = "mpirun -np 1 /n/holystore01/LABS/kozinsky_lab/Lab/Software/LAMMPS/lammps-29Aug2024/a100build/lmp"


def get_enthalpy(atoms):
    """
    Calculate the enthalpy of a structure using LAMMPS with FLARE potential.
    Args:
        atoms (ase.Atoms): The atomic structure to calculate enthalpy for.
    Returns:
        tuple: (pressure in GPa, enthalpy in eV, volume per atom in Angstrom^3, energy per atom in eV, number of atoms)"""
    ## setup in the flare yaml
    # "species_map": {"6": 0, "14": 1}
    # "single_atom_energies": {"0": -9.10091275, "1": -5.42497875},
    mu_c = -9.10091275
    mu_si = -5.42497875

    specorder=["C", "Si"]
    calc, params = get_flare_lammps_calc(
        potfile="../lmp.flare",
        uncfile="../L_inv_lmp.flare ../sparse_desc_lmp.flare",
        # !!! Please download these above two files from https://doi.org/10.5281/zenodo.14648292 'Test_Unc.zip' before running.
        specorder=specorder,
    )

    atoms.calc = calc
    e_total = atoms.get_potential_energy()
    # add energy correction from single atom energies, 
    # assume 1:1 stoichiometry
    e_total += (mu_si + mu_c) * len(atoms) / 2
    # minus sign follows the logic 
    # https://github.com/mir-group/flare/blob/b306fca4a563ef4c0d71a867d3dafd4d50f478a7/flare/md/lammps.py#L333
    pressure = -np.trace(atoms.get_stress(voigt=False)) / 3
    volume = atoms.get_volume()
    enthalpy = e_total + pressure * volume
    return pressure / units.GPa, enthalpy / len(atoms), volume / len(atoms), e_total / len(atoms), len(atoms)


def calculate_enthalpy_vs_a_flare(
    phase_name,
    contcar_file,
    a_range,
    output_txt,
):
    pressures = []
    enthalpies_per_atom = []
    volumes_per_atom = []
    energies_per_atom = []
    num_atoms_list = []

    for a in np.linspace(*a_range):
        atoms = read(contcar_file, format="vasp")
        atoms.set_cell(a * np.eye(3), scale_atoms=True)
        pressure, enthalpy_per_atom, volume_per_atom, e_per_atom, num_atoms = get_enthalpy(atoms)
        print(f"{phase_name}: a={a:.3f}, pressure={pressure:.3f} GPa, enthalpy={enthalpy_per_atom:.3f} eV")
        pressures.append(pressure)
        enthalpies_per_atom.append(enthalpy_per_atom)
        volumes_per_atom.append(volume_per_atom)
        energies_per_atom.append(e_per_atom)
        num_atoms_list.append(num_atoms)

    lattice_a = np.linspace(*a_range)
    pdb.set_trace() 
    # Save all data
    np.savetxt(
        output_txt,
        np.vstack([pressures, enthalpies_per_atom, volumes_per_atom, energies_per_atom, num_atoms_list, lattice_a]).T,
        header="Pressure(GPa) Enthalpy/Atom(eV) Volume/Atom(Angstrom^3) Energy/Atom(eV) Num_Atoms Lattice_a(Angstrom)",
        fmt="%.6f %.6f %.6f %.6f %d %.6f"
    )

#a = 3.586 # for 200 GPa, 3.475 for 300 GPa

def calculate_equilibrium_enthalpy(output_txt, contcar_file, a):
    atoms = read(contcar_file, format="vasp")
    atoms.set_cell(a * np.eye(3), scale_atoms=True)
    pressure, enthalpy_per_atom, volume_per_atom, e_per_atom, num_atoms = get_enthalpy(atoms)
    # append to file
    with open(output_txt, "a") as f:
        f.write(f"{pressure:.6f} {enthalpy_per_atom:.6f} {volume_per_atom:.6f} {e_per_atom:.6f} {num_atoms} {a:.6f}\n")

if __name__ == "__main__":

    ## Generate data for E-V, H-P curve 
    # calculate_enthalpy_vs_a_flare(
    #     phase_name="Rock Salt",
    #     contcar_file="DFT/rs_CONTCAR",
    #     a_range=(3.5, 4.7, 30),
    #     output_txt="rs_enthalpy.txt",
    # )

    # calculate_enthalpy_vs_a_flare(
    #     phase_name="Zincblende",
    #     contcar_file="DFT/zb_CONTCAR",
    #     a_range=(3.5, 4.7, 30),
    #     output_txt="zb_enthalpy.txt",
    # )

    ## Generate equilibrium data
    # calculate_equilibrium_enthalpy("rs_enthalpy.txt", "rs_CONTCAR", a=4.052553)
    # calculate_equilibrium_enthalpy("zb_enthalpy.txt", "zb_CONTCAR", a=4.379279)

    ## Generate data for bulk modulus EOS fitting
    a_eq_rs = 4.052553
    a_eq_zb = 4.379279

    calculate_enthalpy_vs_a_flare(
        phase_name="rs",
        contcar_file="DFT/rs_CONTCAR",
        a_range=(0.98*a_eq_rs, 1.02*a_eq_rs, 40),  # (start, stop, num)
        output_txt="rs_near_equilibrium_0.98_1.02_40.txt",
    )

    calculate_enthalpy_vs_a_flare(
        phase_name="zb",
        contcar_file="DFT/zb_CONTCAR",
        a_range=(0.98*a_eq_zb, 1.02*a_eq_zb, 40),
        output_txt="zb_near_equilibrium_0.98_1.02_40.txt",
    )

    shutil.rmtree("tmp")
