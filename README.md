# SiC phase diagram from machine learning molecular dynamics
This repo includes code for running and analyzing high temperature high pressure molecular dynamics simulations for SiC. It includes some analysis and visualization code for the paper.
The complete dataset is uploaded on Zenodo: 10.5281/zenodo.14648292

## Dependencies

You will need the dependencies specified in `environment.yml`. You can create a conda environment with 

```bash
conda env create -f environment.yml
```

Then a conda env named `sic` will be created. To add the environment to the Kernel of your Jupyter Notebook, run

```bash
python -m ipykernel install --user --name sic --display-name "SiC"
```

To check whether the kernel is installed successfully, run

```bash
jupyter kernelspec list
```

The spatial correlation calculation was computed from voxel density, which is obtained from ParaView. We have uploaded all the generated .vtk files.

## Files

`Plot.ipynb`: the notebook for making figures in the manuscript.

`lmp.flare`: the MLFF coefficient file used by LAMMPS to run MD simulations.

