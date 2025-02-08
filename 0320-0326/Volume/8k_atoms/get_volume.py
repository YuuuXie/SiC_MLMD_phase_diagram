from ovito.io import import_file, export_file
import os, time, sys
import numpy as np

P = int(sys.argv[1])
for i in range(10):
    T0 = 5000 - i * 200
    T1 = 4800 - i * 200

    tic = time.time()
    pipeline = import_file(f"../P{P}/cool_{T0}_{T0}.bin")
    print("import file", time.time() - tic)
    
    tic = time.time()
    cell_list = []
    for frame_index in range(0, pipeline.source.num_frames, 20):
        data = pipeline.source.compute(frame_index)
        cell = data.cell[:, :3]
        cell_list.append(cell.reshape(-1))
    np.savetxt(f"P{P}_{2*i}_cells.txt", np.array(cell_list))
    print("export", time.time() - tic)

    tic = time.time()
    pipeline = import_file(f"../P{P}/cool_{T0}_{T1}.bin")
    print("import file", time.time() - tic)
    
    tic = time.time()
    cell_list = []
    for frame_index in range(0, pipeline.source.num_frames, 20):
        data = pipeline.source.compute(frame_index)
        cell = data.cell[:, :3]
        cell_list.append(cell.reshape(-1))
    np.savetxt(f"P{P}_{2*i+1}_cells.txt", np.array(cell_list))
    print("export", time.time() - tic)
