from ase.calculators.vasp import Vasp
import numpy as np
import shutil
from ase import units
from ase.io import read
import os

tot_ncore = os.environ['SLURM_NTASKS']
os.environ["ASE_VASP_COMMAND"]=f"mpirun -np {tot_ncore} /n/holystore01/LABS/kozinsky_lab/Lab/Software/VASP6.3-GNU/vasp.6.3.0/bin/vasp_std"
os.environ["VASP_PP_PATH"]="/n/holystore01/LABS/kozinsky_lab/Lab/Software/VASP6.3-GNU/Potentials_54"
print(f"total ncore={tot_ncore}")

def run_vasp_and_save(atoms, directory, post_fix, kpts=[6,6,6]):
    """
    Run VASP calculation using ASE, save pressure, enthalpy, per atom volume, per atom energy, number of atoms 
    """
    calc = Vasp(
        directory=directory,
        xc='PBE',
        encut=1400,
        gamma=True,
        kpts=kpts,
        sigma=0.03,
        ediff=1e-8,
        algo='Very_Fast',
        prec='Accurate',
        ismear=0,
        istart=1,
        isym=1,
        npar=4,
        lplane=True,
        lreal=False,
    )
    atoms.calc = calc

    # Run calculation
    energy = atoms.get_potential_energy()
    forces = atoms.get_forces()
    stress = atoms.get_stress(voigt=False)
    pressure = -np.trace(stress) / 3 / units.GPa # GPa
    volume = atoms.get_volume()
    enthalpy = energy + (-np.trace(stress) / 3) * volume

    # Save OUTCAR for later comparison
    outcar_src = f"{directory}/OUTCAR"      
    outcar_dst = f"{directory}/OUTCAR_{post_fix}"
    shutil.copy(outcar_src, outcar_dst)

    return pressure, enthalpy / len(atoms), volume / len(atoms), energy / len(atoms), len(atoms)

def calculate_enthalpy_vs_a(
    phase_name,
    contcar_file,
    a_range,
    output_prefix,
    kpts=[6,6,6]
):
    pressures = []
    enthalpies_per_atom = []
    volumes_per_atom = []
    energies_per_atom = []
    num_atoms_list = []

    directory = f"{output_prefix}_dft"
    os.makedirs(directory, exist_ok=True)

    for a in np.linspace(*a_range):
        atoms = read(contcar_file, format="vasp")
        atoms.set_cell(a * np.eye(3), scale_atoms=True)
        pressure, enthalpy_per_atom, volume_per_atom, e_per_atom, num_atoms = run_vasp_and_save(
            atoms=atoms,
            directory=directory,
            post_fix=f"{output_prefix}_a{a:.3f}",
            kpts=kpts
        )
        print(f"{phase_name}: a={a:.3f}, pressure={pressure:.3f} GPa, enthalpy={enthalpy_per_atom:.3f} eV")
        pressures.append(pressure)
        enthalpies_per_atom.append(enthalpy_per_atom)
        volumes_per_atom.append(volume_per_atom)
        energies_per_atom.append(e_per_atom)
        num_atoms_list.append(num_atoms)

    lattice_a = np.linspace(*a_range)
    np.savetxt(
        f"{output_prefix}_enthalpy_dft.txt",
        np.vstack([pressures, enthalpies_per_atom, volumes_per_atom, energies_per_atom, num_atoms_list, lattice_a]).T,
        header="Pressure(GPa) Enthalpy/Atom(eV) Volume/Atom(Angstrom^3) Energy/Atom(eV) Num_Atoms Lattice_a(Angstrom)",
        fmt="%.6f %.6f %.6f %.6f %d %.6f"
    )


def calculate_equilibrium_enthalpy(phase_name, contcar_file, a, kpts=[6,6,6]):
    atoms = read(contcar_file, format="vasp")
    atoms.set_cell(a * np.eye(3), scale_atoms=True)
    pressure, enthalpy_per_atom, volume_per_atom, e_per_atom, num_atoms = run_vasp_and_save(
        atoms=atoms,
        directory=f"{phase_name}_dft",
        post_fix=f"{phase_name}_equilibrium",
        kpts=kpts
    )
    # append to file
    with open(f"{phase_name}_enthalpy_dft.txt", "a") as f:
        f.write(f"{pressure:.6f} {enthalpy_per_atom:.6f} {volume_per_atom:.6f} {e_per_atom:.6f} {num_atoms} {a:.6f}\n")

if __name__ == "__main__":

    ## Generate data for E-V, H-P curve 
    # calculate_enthalpy_vs_a(
    #     phase_name="rs",
    #     contcar_file="rs_CONTCAR",
    #     a_range=(3.5, 4.7, 30),  # (start, stop, num)
    #     output_prefix="rs",
    #     kpts=[6,6,6]
    # )

    # calculate_enthalpy_vs_a(
    #     phase_name="zb",
    #     contcar_file="zb_CONTCAR",
    #     a_range=(3.5, 4.7, 30),
    #     output_prefix="zb",
    #     kpts=[6,6,6]
    # )

    ## Generate equilibrium data
    # calculate_equilibrium_enthalpy(
    #     phase_name="rs",
    #     contcar_file="rs_CONTCAR",
    #     a=4.052553,
    #     kpts=[6, 6, 6]
    # )

    # calculate_equilibrium_enthalpy(
    #     phase_name="zb",
    #     contcar_file="zb_CONTCAR",
    #     a=4.379279,
    #     kpts=[6, 6, 6]
    # )

    ## Generate data for bulk modulus EOS fitting
    a_eq_rs = 4.052553
    a_eq_zb = 4.379279

    calculate_enthalpy_vs_a(
        phase_name="rs",
        contcar_file="rs_CONTCAR",
        a_range=(0.98*a_eq_rs, 1.02*a_eq_rs, 40),  # (start, stop, num)
        output_prefix="rs_near_equilibrium_0.98_1.02_40",
        kpts=[6,6,6]
    )

    calculate_enthalpy_vs_a(
        phase_name="zb",
        contcar_file="zb_CONTCAR",
        a_range=(0.98*a_eq_zb, 1.02*a_eq_zb, 40),
        output_prefix="zb_near_equilibrium_0.98_1.02_40",
        kpts=[6,6,6]
    )