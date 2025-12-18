# Example to extract cluster size data using OVITO's Python API
# Need to provide trajectory dump files, cannot be ran directly in this directory
from ovito.io import import_file, export_file
from ovito.modifiers import ClusterAnalysisModifier, SelectTypeModifier
import sys, time

# Load static topology data from a LAMMPS data file.
P = 90
T = 3800
base_dir = 'decomposed'  # 'supercool_SiC' or 'decomposed'
print(P, T)
if base_dir == 'supercool_SiC':
    file_choice =  ["1start", "2cooldown", "3coolend"]
elif base_dir == 'decomposed':
    file_choice =  [f"cool_{T}_{T}", f"heat_{T}_{T}"]
for i, file in enumerate(file_choice):
    tic = time.time()
    if base_dir == 'supercool_SiC':
        pipeline = import_file(f'{base_dir}/P{P}_T{T}/{file}.bin')
    elif base_dir == 'decomposed':
        pipeline = import_file(f'{base_dir}/P{P}/{file}.bin')
    modifier = SelectTypeModifier(property = 'Particle Type', types = {'Type 1'})
    pipeline.modifiers.append(modifier)
    pipeline.modifiers.append(
        ClusterAnalysisModifier(
            cutoff=1.6,
            sort_by_size=True, 
            only_selected=True,
        )
    )

    export_file(
        pipeline, 
        f"{base_dir}/P{P}/T{T}_clusters{i+1}.txt", 
        "txt/attr", 
        multiple_frames=True, 
        start_frame=0, 
        end_frame=pipeline.source.num_frames - 1, 
        every_nth_frame=1, 
        columns=["ClusterAnalysis.largest_size"],
    )
    print(i, time.time() - tic)
