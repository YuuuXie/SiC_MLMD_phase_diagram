from ovito.io import import_file, export_file
from ovito.modifiers import ClusterAnalysisModifier, SelectTypeModifier
import sys, time

# Load static topology data from a LAMMPS data file.
P = sys.argv[1]
T = sys.argv[2]
print(P, T)

if P in ["10", "20"]:
    n_stage = {
        "1equil": 1, "2heathalf": 2, "3coolhalf": 3, "5nph_continue": 4
    }
else:
    n_stage = {
        "1equil": 1, "2heathalf": 2, "3coolhalf": 3, "4nph": 4
    }

for stage_name, stage_num in n_stage.items():
    tic = time.time()
    pipeline = import_file(f'P{P}/T{T}/{stage_name}.bin')
    num_frames = pipeline.source.num_frames
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
        f"P{P}_T{T}_clusters{stage_num}.txt", 
        "txt/attr", 
        multiple_frames=True, 
        start_frame=0, 
        end_frame=num_frames-1, 
        every_nth_frame=10, 
        columns=["ClusterAnalysis.largest_size"],
    )
    print(f"Stage {stage_name} -> {stage_num}: {time.time() - tic:.1f}s")
