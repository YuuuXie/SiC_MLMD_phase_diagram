from ovito.io import import_file, export_file
import time, sys

P = int(sys.argv[1])
T = int(sys.argv[2])

tic = time.time()
#pipeline = import_file(f'../No_Defect/P{P}/T{T}/4nph.bin')
pipeline = import_file(f'../No_Defect_RS/T{T}/4nph.bin')
export_file(
    pipeline, 
    f"P{P}0000_T{T}_RS_4nph.txt", 
    "lammps/dump", 
    columns = ["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"],
    multiple_frames=True,
    every_nth_frame=100,
)
print(time.time() - tic)
