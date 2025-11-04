import os
from ovito.io import import_file, export_file
from ovito.modifiers import PolyhedralTemplateMatchingModifier, IdentifyDiamondModifier, ClusterAnalysisModifier, SelectTypeModifier
from ovito.data import DataTable
import sys, time
import numpy as np  


def diamond_outside_clusters(frame, data, threshold=100):
    """Mark cubic-diamond carbon atoms (Structure Type == 1, Particle Type == 1)
    that are NOT in any cluster listed in data.tables['clusters'].
    Creates particle property 'DiamondOutsideCluster' with 1 (outside) or 0 (inside)."""

    # Show a status text in the status bar:
    yield 'Identifying diamond atoms outside clusters...'

    pts = data.particles
    structure = pts['Structure Type'].array
    ptype = pts['Particle Type'].array
    cluster_ids = pts['Cluster'].array

    # diamond cubic atoms
    Si_diamond_mask = (ptype == 2) & (structure == 1)  # include both Si and C cubic diamond
    C_diamond_mask = (ptype == 1) & (structure == 1) # only carbon cubic diamond

    # collect large cluster ids reported by the ClusterAnalysisModifier
    if 'clusters' in data.tables:
        all_cluster_ids = data.tables['clusters']['Cluster Identifier'].array
        large_cluster_mask = data.tables['clusters']['Cluster Size'].array > threshold
        large_cluster_ids = set(all_cluster_ids[large_cluster_mask])
    else:
        large_cluster_ids = set()

    # count carbon diamond atoms whose cluster id is NOT in the large_cluster_ids
    C_diamond_cluster_ids = cluster_ids[C_diamond_mask]
    outside_mask = ~np.isin(C_diamond_cluster_ids, list(large_cluster_ids))
    C_diamond_outside = np.sum(outside_mask)
    diamond_outside = C_diamond_outside + np.sum(Si_diamond_mask)

    table = data.tables.create(identifier='diamond-outside', plot_mode=DataTable.PlotMode.BarChart, title='Count Diamond-like Atoms Outside Carbon Clusters')
    table.x = table.create_property('Structure Type', data=[0, 1])
    table.x.add_type_id(0, table, name='Cubic Diamond')
    table.x.add_type_id(1, table, name='Cubic Diamond Outside Carbon Clusters')
    table.y = table.create_property('Count', data=[np.sum(Si_diamond_mask) + np.sum(C_diamond_mask), diamond_outside])


sim_folder = "64K_ZB" # specify simulation folder: "128K_ZB", "64K_ZB", "16K_solid_ZB", "16K_solid_RS"

if "RS" in sim_folder:
    target = "rocksalt" 
    Pressure_to_Temp = {
        85: [4400, 4500, 4600, 4700],
        90: [4500, 4700],
        100: [4900, 5000, 5100, 5200]
        }
elif "ZB" in sim_folder:
    target = "zincblende"
    if "128K" in sim_folder or "64K" in sim_folder:
        Pressure_to_Temp = {
            30: [3200, 3400, 3600, 3800],
            60: [3200, 3400, 3600, 3800],
            }
    elif "16K_solid_ZB" in sim_folder:
        Pressure_to_Temp = {
            10: [2900, 3000, 3100, 3200],
            20: [3200, 3300, 3400, 3500],
            45: [3500, 3600, 3700, 3800],
            70: [3400, 3500, 3600, 3700],
            80: [3300, 3400, 3500, 3600]
            }
    elif "exist_sim" in sim_folder:
        Pressure_to_Temp = {
            30: [3200, 3400, 3600, 3800],
            60: [3200, 3400, 3600, 3800],
            }
else:
    raise ValueError("sim_folder must contain either 'RS' or 'ZB'")
# Load static topology data from a LAMMPS data file.

            
if target == "rocksalt":
    find_struct = PolyhedralTemplateMatchingModifier(rmsd_cutoff=0.2)
    find_struct.structures[PolyhedralTemplateMatchingModifier.Type.SC].enabled = True
    find_struct.structures[PolyhedralTemplateMatchingModifier.Type.FCC].enabled = False
    find_struct.structures[PolyhedralTemplateMatchingModifier.Type.BCC].enabled = False
    find_struct.structures[PolyhedralTemplateMatchingModifier.Type.HCP].enabled = False
elif target == "zincblende":
    find_struct = IdentifyDiamondModifier()


for P in Pressure_to_Temp.keys():
    if P in [10, 20]:
        n_stage = {
            "1equil": 1, "2heathalf": 2, "3coolhalf": 3, "5nph_continue": 4
        }
    else:
        n_stage = {
            "1equil": 1, "2heathalf": 2, "3coolhalf": 3, "4nph": 4
        }
    for T in Pressure_to_Temp[P]:
        print(f"P = {P}, T = {T}")
        for stage_name, stage_num in n_stage.items():
            tic = time.time()
            pipeline = import_file(f'{sim_folder}/P{P}/T{T}/{stage_name}.bin')
            num_frames = pipeline.source.num_frames
            pipeline.modifiers.append(find_struct)
            
            # Count cubic diamond atoms outside large carbon clusters  
            if target == "zincblende":

                # Add cluster analysis
                modifier = SelectTypeModifier(property = 'Particle Type', types = {'Type 1'})
                pipeline.modifiers.append(modifier)
                pipeline.modifiers.append(
                    ClusterAnalysisModifier(
                        cutoff=1.6,
                        sort_by_size=True, 
                        only_selected=True,
                    )
                )
                # Count diamond atoms outside large carbon clusters
                pipeline.modifiers.append(diamond_outside_clusters)

                os.makedirs(f"{sim_folder}", exist_ok=True)
                export_file(
                    pipeline, 
                    f"{sim_folder}/P{P}_T{T}_{target}{stage_num}.txt", "txt/table", 
                    key='diamond-outside',
                    multiple_frames=True, 
                    start_frame=0, 
                    end_frame=num_frames-1, 
                    every_nth_frame=10)
                print(f"Stage {stage_name} -> {stage_num}: {time.time() - tic:.1f}s")
