#!/bin/sh
#SBATCH -n 18
#SBATCH -N 1
#SBATCH --cpus-per-task=2
#SBATCH -t 8:00:00
#SBATCH -p seas_compute
#SBATCH --mem-per-cpu=3500

module load cmake/3.17.3-fasrc01
module load gcc/9.3.0-fasrc01
module load intel-mkl/2017.2.174-fasrc01
module load openmpi/4.0.5-fasrc01

export OMP_NUM_THREADS=1

#srun -n ${SLURM_NTASKS} --mpi=pmi2 /n/home08/xiey/lammps-stable_29Sep2021_update3/build_noomp/lmp -v P $((P*10000)) -v T 4000 -in in.lammps
mpirun -n ${SLURM_NTASKS} /n/home08/xiey/lammps-stable_29Sep2021_update3/build_noomp/lmp -v P $((P*10000)) -v T $T -in in.lammps
