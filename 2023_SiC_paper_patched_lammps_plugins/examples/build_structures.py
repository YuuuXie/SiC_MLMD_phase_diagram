"""Build SiC zinc-blende and rock-salt conventional cells, write LAMMPS data files
with two species orderings so we can pick the right one based on cohesive energy."""
from ase.build import bulk
from ase.io import write
from ase import Atoms
import numpy as np

# Zinc-blende SiC (3C-SiC): a ≈ 4.36 Å experimentally
zb = bulk('SiC', 'zincblende', a=4.36, cubic=True)  # 8-atom conventional cell
print("ZB cell:", zb.cell.lengths(), "natoms:", len(zb), "symbols:", zb.get_chemical_symbols())

# Rock-salt SiC: high-pressure phase, a ≈ 4.06 Å (DFT)
rs = bulk('SiC', 'rocksalt', a=4.06)  # primitive 2-atom cell
# Make it conventional 8-atom cubic for clarity
rs_conv = Atoms(symbols=['Si','C','Si','C','Si','C','Si','C'],
                scaled_positions=[(0,0,0),(0.5,0,0),(0,0.5,0),(0,0,0.5),
                                  (0.5,0.5,0),(0.5,0,0.5),(0,0.5,0.5),(0.5,0.5,0.5)],
                cell=[4.06,4.06,4.06], pbc=True)
print("RS cell:", rs_conv.cell.lengths(), "natoms:", len(rs_conv), "symbols:", rs_conv.get_chemical_symbols())

def write_lammps_data(atoms, filename, type_map):
    """Write LAMMPS data file with atom types ordered by type_map={symbol: type_id}."""
    symbols = atoms.get_chemical_symbols()
    types = [type_map[s] for s in symbols]
    cell = atoms.get_cell()
    positions = atoms.get_positions()
    n_types = max(type_map.values())
    with open(filename, 'w') as f:
        f.write("LAMMPS data file\n\n")
        f.write(f"{len(atoms)} atoms\n")
        f.write(f"{n_types} atom types\n\n")
        f.write(f"0.0 {cell[0,0]:.10f} xlo xhi\n")
        f.write(f"0.0 {cell[1,1]:.10f} ylo yhi\n")
        f.write(f"0.0 {cell[2,2]:.10f} zlo zhi\n")
        # tilt (orthogonal in our case)
        xy, xz, yz = cell[1,0], cell[2,0], cell[2,1]
        if abs(xy)+abs(xz)+abs(yz) > 1e-8:
            f.write(f"{xy:.10f} {xz:.10f} {yz:.10f} xy xz yz\n")
        f.write("\nAtoms\n\n")
        for i, (t, p) in enumerate(zip(types, positions), 1):
            f.write(f"{i} {t} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n")

# Si=1, C=2 ordering
write_lammps_data(zb, 'zb_sic1.data', {'Si':1, 'C':2})
write_lammps_data(rs_conv, 'rs_sic1.data', {'Si':1, 'C':2})
# C=1, Si=2 ordering
write_lammps_data(zb, 'zb_sic2.data', {'C':1, 'Si':2})
write_lammps_data(rs_conv, 'rs_sic2.data', {'C':1, 'Si':2})
print("Wrote 4 data files")
