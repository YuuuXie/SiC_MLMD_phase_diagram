import ovito
from ovito.io import import_file, export_file
import matplotlib.pyplot as plt
import math, time
from ovito.vis import Viewport
from IPython.display import Image
from ovito.vis import TachyonRenderer
from ovito.modifiers import ComputePropertyModifier, PolyhedralTemplateMatchingModifier

# Change red and blue atoms to Si and C
tic = time.time()
trjname = "3coolend_1_shorter"
pipeline = import_file(f"{trjname}.lammpstrj")
pipeline.modifiers.append(ComputePropertyModifier(output_property='Radius', expressions=['(ParticleType==1)*0.78+(ParticleType==2)*1.18']))
pipeline.modifiers.append(ComputePropertyModifier(output_property='Color', expressions=[
    '(ParticleType==1)*0.5+(ParticleType==2)*0.9',
    '(ParticleType==1)*0.5+(ParticleType==2)*0.75',
    '(ParticleType==1)*0.5+(ParticleType==2)*0.55',
]))
print("load", time.time() - tic)

##Calculate per-particle displacements with respect to initial simulation frame:
#ptm = PolyhedralTemplateMatchingModifier()
#ptm.rmsd_cutoff = 0.16
#ptm.structures[PolyhedralTemplateMatchingModifier.Type.SC].enabled = True
#ptm.structures[PolyhedralTemplateMatchingModifier.Type.CUBIC_DIAMOND].enabled = True
#ptm.structures[PolyhedralTemplateMatchingModifier.Type.GRAPHENE].enabled = True
#pipeline.modifiers.append(ptm)

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
for i in range(pipeline.source.num_frames):
    tic = time.time()
    figfile = f"{trjname}_{i}.png"
    vp.render_image(filename=figfile, background=(1,1,1), size=(2000, 2000), alpha=1.0, frame=i) #, renderer=tachyon)
    print("render", i, time.time() - tic)

#Image(figfile)
