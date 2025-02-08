from ovito.io import import_file, export_file
from ovito.modifiers import ComputePropertyModifier, SpatialBinningModifier, HistogramModifier
import os, time, sys

def get_histogram(P, trjname):
    tic = time.time()
    pipeline = import_file(trjname)
    print("import file", time.time() - tic)
    
    tic = time.time()
    pipeline.modifiers.append(ComputePropertyModifier(expressions=['1*(ParticleType==6)'], output_property='Unity'))
    
    bin_size = 40
    pipeline.modifiers.append(SpatialBinningModifier(
        property = 'Unity',
        direction = SpatialBinningModifier.Direction.XYZ, 
        bin_count = (bin_size, bin_size, bin_size),
        reduction_operation = SpatialBinningModifier.Operation.Sum
    ))
    export_file(pipeline, 'density_*.vtk', 'vtk/grid', key='binning', multiple_frames=True, every_nth_frame=10)
    #data = pipeline.compute()
    ##print(data.grids.keys())
    ##print(dir(data.grids['binning']["Unity"]))
    print("compute", time.time() - tic)
    #
    #tic = time.time()
    #modifier = HistogramModifier(bin_count=10, property='Unity', operate_on="voxels", fix_xrange=True, xrange_start=0.0, xrange_end=1.0)
    #pipeline.modifiers.append(modifier)
    #
    #export_file(pipeline, f"P{P}_{trjname}.txt", "txt/table", key="histogram[Unity]", multiple_frames=True)
    #print("export", time.time() - tic)


os.environ["OVITO_THREAD_COUNT"] = "32"

P = int(sys.argv[1])
dump = sys.argv[2]
trjname = f"../Nucleation/P{P}_{dump}_cluster_ovito.xyz"
get_histogram(P, trjname)
