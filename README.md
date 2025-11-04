# SiC phase diagram from machine learning molecular dynamics (MLMD)
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

## Plotting Solid-Decomposed Phase Coexistence MLMD Results

To reproduce two-phase analysis plots for SiC simulations, use `plot_two_phase.py`:

1. Make sure the simulation folder exists (e.g., `16K_solid_ZB`, `16K_solid_RS`, etc.).
2. Run `plot_two_phase.py` with the following command:

	```bash
	python plot_two_phase.py --file_path 16K_solid_ZB --plot_press True
	```

	- The script will automatically detect the simulation type and number of atoms.
	- The output plot will be saved in the specified folder.

Optional: Add `--moving_avg` to smooth temperature and pressure data.

### Simulation Folders

- `16K_solid_ZB`: Two-phase simulations with 16,000 atoms starting from Zinc Blende (B3) solid and resulting B3 $\leftrightarrow$ decomposed Si + C coexistence.
- `16K_solid_RS`: Two-phase simulations with 16,000 atoms starting from Rock Salt (B1) solid and resulting B1 $\leftrightarrow$ liquid coexistence.
- `64K_ZB`: Two-phase simulations with 64,000 atoms with B3 $\leftrightarrow$ decomposed Si + C coexistence.
- `128K_ZB`: Two-phase simulations with 128,000 atoms with B3 $\leftrightarrow$ decomposed Si + C coexistence.

## Plotting Liquid-Decomposed Phase Coexistence MLMD Results

To reproduce liquid-decomposed two-phase analysis plots for SiC simulations, use `plot_liquid_two_phase.py`:
1. Make sure the simulation folder exists (e.g., `16K_liquid`).
2. Run `plot_liquid_two_phase.py` with the following command:
3. ```bash
   python plot_liquid_two_phase.py --file_path 16K_liquid --plot_press True
   ```
   - The output plot will be saved in the specified folder.
  
Optional: Add `--moving_avg` to smooth temperature and pressure data.

## Plotting SiC Phase Diagram

To reproduce the SiC phase diagram plot, use `plot_phase_diagram.py`:
```bash
python plot_phase_diagram.py
```
This will generate a png file of the phase diagram in `./phase_diagram/SiC_phase_diagram.png`.

## Check 512k-atom MLMD Simulation

To check whether identified diamond structures are in the carbon nanoclusters of the 512k-atom cooling MLMD simulations, we use `check_diamond_in_C_clusters.py`. Run the script with:
```bash
python check_diamond_in_C_clusters.py
```
and it will read from `0123-0129/512k_atoms_cool/P{pressure}/` folders. The output will be printed in the terminal.


## Gas Phase Simulations

Gas phase simulations are performed to study the behavior of SiC at low pressures and high temperatures.

### Folder Structure
- `gas_phase/`: Contains simulation data and analysis scripts for the gas phase.
	- `plot_volume.py`: Script to plot the volume of the system across varied pressures and temperatures.
	- `gas_phase_logs/`: LAMMPS log files.


