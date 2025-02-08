from ovito.io import import_file, export_file
import os, time, sys
import numpy as np

P = int(sys.argv[1])
trjname = sys.argv[2]

tic = time.time()
pipeline = import_file(f"P{P}/{trjname}")
print("import file", time.time() - tic)

tic = time.time()
cell_list = []
for frame_index in range(pipeline.source.num_frames):
    data = pipeline.source.compute(frame_index)
    cell = data.cell[:, :3]
    cell_list.append(cell.reshape(-1))
np.savetxt(f"P{P}_{trjname.split('.')[0]}_cells.txt", np.array(cell_list))
print("export", time.time() - tic)
