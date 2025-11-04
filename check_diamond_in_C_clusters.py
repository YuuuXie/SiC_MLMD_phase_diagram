import ovito
from ovito.io import import_file, export_file
import matplotlib.pyplot as plt
import math
from ovito.vis import Viewport
from IPython.display import Image
from ovito.vis import TachyonRenderer

from ovito.modifiers import ComputePropertyModifier, PolyhedralTemplateMatchingModifier
from ovito.modifiers import ClusterAnalysisModifier, SelectTypeModifier
import numpy as np

# Change red and blue atoms to Si and C
for P in [30, 60, 80]:
    path = f"0123-0129/512k_atoms_cool/P{P}"
    print("Pressure:", P, "GPa")
    pipeline = import_file(f"{path}/3coolend_final.xyz")
    pipeline.modifiers.append(ComputePropertyModifier(output_property='Radius', expressions=['(ParticleType==1)*0.78+(ParticleType==2)*1.18']))
    pipeline.modifiers.append(ComputePropertyModifier(output_property='Color', expressions=[
        '(ParticleType==1)*0.5+(ParticleType==2)*0.9',
        '(ParticleType==1)*0.5+(ParticleType==2)*0.75',
        '(ParticleType==1)*0.5+(ParticleType==2)*0.55',
    ]))

    #Calculate per-particle displacements with respect to initial simulation frame:
    ptm = PolyhedralTemplateMatchingModifier()
    ptm.rmsd_cutoff = 0.16
    ptm.structures[PolyhedralTemplateMatchingModifier.Type.SC].enabled = True
    ptm.structures[PolyhedralTemplateMatchingModifier.Type.CUBIC_DIAMOND].enabled = True
    ptm.structures[PolyhedralTemplateMatchingModifier.Type.GRAPHENE].enabled = True
    pipeline.modifiers.append(ptm)

    modifier = SelectTypeModifier(property = 'Particle Type', types = {'Type 1'})
    pipeline.modifiers.append(modifier)
    pipeline.modifiers.append(
        ClusterAnalysisModifier(
            cutoff=1.6,
            sort_by_size=True, 
            only_selected=True,
        )
    )

    data = pipeline.compute()

    # Get arrays for particle type and structure type
    particle_types = data.particles['Particle Type'].array
    structure_types = data.particles['Structure Type'].array  # Added by PTM modifier
    cluster_ids = data.particles['Cluster'].array
    num_atoms = len(particle_types)

    # Map structure type integer to names
    type_map = {
        5: "SC",
        6: "CUBIC_DIAMOND",
        8: "GRAPHENE"
    }

    # Only consider carbon atoms (Type 1)
    carbon_indices = (particle_types == 1)
    carbon_structures = structure_types[carbon_indices]

    # Exam the cluster id of diamond, graphene type of carbon atoms
    # diamond_graphene_indices = carbon_indices & ((structure_types == 6) | (structure_types == 8))
    diamond_graphene_indices = carbon_indices & (structure_types == 6)
    diamond_graphene_cluster_ids = cluster_ids[diamond_graphene_indices]

    # Select clusters with size > threshold
    threshold = 100 # number of atoms in the cluster
    cluster_table = data.tables["clusters"]
    large_cluster_mask = cluster_table["Cluster Size"].array > threshold
    large_cluster_ids = cluster_table["Cluster Identifier"].array[large_cluster_mask]

    # Filter diamond/graphene carbon atoms that belong to large clusters
    cluster_id_set, counts = np.unique(diamond_graphene_cluster_ids, return_counts=True)
    total_counts = sum(counts)
    in_large_cluster_mask = np.isin(cluster_id_set, large_cluster_ids)
    print(f"Identified fraction of diamond/graphene carbon atoms: {total_counts/num_atoms*2*100} %")
    print(f"Ratio of diamond/graphene carbon atoms in large clusters: {sum(counts[in_large_cluster_mask]) / total_counts:.4f}")
    print("Large cluster size:", cluster_table["Cluster Size"].array[large_cluster_mask])

cell_vis = pipeline.source.data.cell.vis
cell_vis.line_width = 0.2
cell_vis.rendering_color = (0.3, 0.3, 0.3)

# Plot
del ovito.scene.pipelines[:]
pipeline.add_to_scene()

vp = Viewport()
vp.type = Viewport.Type.Front
#vp.camera_pos = (-10, -15, 15)
vp.camera_dir = (2, 3, -1)
#vp.fov = math.radians(60.0)
vp.zoom_all()

tachyon = TachyonRenderer(shadows=False, direct_light_intensity=1.1)
figfile = f"{path}/figure_ptm_test.png"
vp.render_image(filename=figfile, background=(1,1,1), renderer=tachyon, size=(2000, 2000), alpha=1.0)

Image(figfile)