# SiC phase diagram from machine learning molecular dynamics
This repo includes code for running and analyzing molecular dynamics simulations for SiC.

## Dependencies

You will need the dependencies specified in `environment.yml`. You can create a conda environment with 

```bash
conda env create -f environment.yml
```

Then a conda env named `sic` will be created. 

The spatial correlation calculation was computed from voxel density, which is obtained from ParaView. We have uploaded all the generated .vtk files.

## Files

`Plot.ipynb`: the notebook for making figures in the manuscript.

`lmp.flare`: the MLFF coefficient file used by LAMMPS to run MD simulations.

