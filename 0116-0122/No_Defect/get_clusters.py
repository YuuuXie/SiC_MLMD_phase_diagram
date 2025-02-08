from ovito.io import import_file, export_file
from ovito.modifiers import ClusterAnalysisModifier, SelectTypeModifier
import sys, time

# Load static topology data from a LAMMPS data file.
P = sys.argv[1]
T = sys.argv[2]
print(P, T)
for i in ["1equil", "2heathalf", "3coolhalf", "4nph"]:
    tic = time.time()
    pipeline = import_file(f'P{P}/T{T}/{i}.bin')
    modifier = SelectTypeModifier(property = 'Particle Type', types = {'Type 1'})
    pipeline.modifiers.append(modifier)
    pipeline.modifiers.append(
        ClusterAnalysisModifier(
            cutoff=1.6,
            sort_by_size=True, 
            only_selected=True,
        )
    )
    #export_file(pipeline, f"T{T}/clusters{i[0]}.*", "txt/table", multiple_frames=True, start_frame=0, end_frame=1000, every_nth_frame=10, key='clusters')
    export_file(
        pipeline, 
        f"P{P}_T{T}_clusters{i[0]}.txt", 
        "txt/attr", 
        multiple_frames=True, 
        start_frame=0, 
        end_frame=1000, 
        every_nth_frame=10, 
        columns=["ClusterAnalysis.largest_size"],
    )
    print(i, time.time() - tic)
