from ase.build import bulk
from ase import Atoms
from ase.io import write

def write_lammps_data(atoms, filename, type_map):
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
        f.write(f"0.0 {cell[2,2]:.10f} zlo zhi\n\n")
        f.write("Atoms\n\n")
        for i, (t, p) in enumerate(zip(types, positions), 1):
            f.write(f"{i} {t} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f}\n")

# 2x2x2 supercell of conventional ZB (a=4.379, 8 atoms/conv) -> 64 atoms
zb = bulk('SiC', 'zincblende', a=4.379, cubic=True).repeat((2,2,2))
print("ZB super:", zb.cell.lengths(), len(zb), "atoms")
write_lammps_data(zb, 'zb_super.data', {'Si':1, 'C':2})

# 2x2x2 supercell of RS conventional (a=4.331, 8 atoms/conv) -> 64 atoms
rs_conv_pos = [(0,0,0),(0.5,0,0),(0,0.5,0),(0,0,0.5),
               (0.5,0.5,0),(0.5,0,0.5),(0,0.5,0.5),(0.5,0.5,0.5)]
rs_conv_sym = ['Si','C','Si','C','Si','C','Si','C']
rs_conv = Atoms(symbols=rs_conv_sym, scaled_positions=rs_conv_pos,
                cell=[4.331,4.331,4.331], pbc=True)
rs_super = rs_conv.repeat((2,2,2))
print("RS super:", rs_super.cell.lengths(), len(rs_super), "atoms")
write_lammps_data(rs_super, 'rs_super.data', {'Si':1, 'C':2})
