from ovito.io import import_file, export_file
from ovito.modifiers import CalculateDisplacementsModifier, SelectTypeModifier
import numpy as np
import time, sys, os

def SelectedMSDModifier(frame, data):
    displacement_magnitudes = data.particles['Displacement Magnitude'][data.particles['Selection'] == 1]
    msd = np.sum(displacement_magnitudes ** 2) / len(displacement_magnitudes)
    data.attributes["MSD"] = msd 

os.environ["OVITO_THREAD_COUNT"] = "48"

tic = time.time()
P = int(sys.argv[1])
species_map = {"C": 1, "Si": 2}
#species_map = {"C": 6, "Si": 14}
elem = sys.argv[2]
species = species_map[elem]
trjname = sys.argv[3]

pipeline = import_file(f"../P{P}/{trjname}.bin")
#pipeline = import_file(f"../Nucleation/P{P}_{trjname}.xyz")
print("load data", time.time() - tic, flush=True)

tic = time.time()
modifier = SelectTypeModifier(property = 'Particle Type', types = {f'Type {species}'})
pipeline.modifiers.append(modifier)
pipeline.modifiers.append(CalculateDisplacementsModifier())
pipeline.modifiers.append(SelectedMSDModifier)

export_file(pipeline, f"P{P}_{trjname}_{elem}_msd.txt", 
    format = "txt/attr",
    columns = ["MSD"],
    multiple_frames = True)
print("compute msd", time.time() - tic)
