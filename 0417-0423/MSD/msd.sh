#!/bin/sh
#SBATCH -p seas_compute
#SBATCH -t 1-00:00
#SBATCH -n 48
#SBATCH -N 1
#SBATCH --mem=0

module load Anaconda3/5.0.1-fasrc01 intel-mkl/2019.5.281-fasrc01 cmake/3.23.2-fasrc01 gcc/10.2.0-fasrc01 openmpi/4.1.0-fasrc01
source activate numba

export OMP_NUM_THREADS=48
python msd.py ${P} ${elem} ${trj}
