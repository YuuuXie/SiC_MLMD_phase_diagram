#!/bin/sh
#SBATCH -p seas_gpu
#SBATCH -t 96:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem-per-cpu=10000
#SBATCH --constraint=a100


module load cmake/3.17.3-fasrc01
module load gcc/9.3.0-fasrc01
module load intel-mkl/2017.2.174-fasrc01
module load openmpi/4.0.5-fasrc01
module load cuda/11.4.2-fasrc01

#export OMP_NUM_THREADS=1

mkdir T${T}
cd T${T}
cp ../in.lammps .
cp ../data.lammps .
cp ../*.flare .
#srun -n ${SLURM_NTASKS} --mpi=pmi2 /n/home08/xiey/lammps-stable_29Sep2021_update3/build_noomp/lmp -v P $((P*10000)) -v T $T -in in.lammps
#/n/kozinsky_lab/Users/xiey/lammps-stable_23Jun2022/build_kokkos/lmp -sf kk -k on g 4 t 8 -pk kokkos newton on neigh full -v P $((P*10000)) -in in.lammps
srun -n ${SLURM_NTASKS} --mpi=pmi2 /n/kozinsky_lab/Users/xiey/lammps-stable_23Jun2022_update1/build/lmp -sf kk -k on g 1 t 8 -pk kokkos newton on neigh full -v P $((P*10000)) -v T $T -in in.lammps
