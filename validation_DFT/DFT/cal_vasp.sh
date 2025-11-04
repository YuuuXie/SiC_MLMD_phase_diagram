#!/bin/bash
#SBATCH --job-name=SiC # Job name
#SBATCH -p kozinsky,seas_compute
##SBATCH --constraint=holyhdr,icelake # icelake has 64, cascadelake has 48
#SBATCH -N 1 # Number of nodes requested
#SBATCH -n 16 # Number of tasks
#SBATCH -c 1 # Number of cores per task
#SBATCH -t 07-00:00 # Runtime in minutes
#SBATCH --mem-per-cpu=2000 # Memory per cpu in MB (see also--mem) 3800 5000
#SBATCH -o logs/%x_%j.out # Standard out goes to this file
#SBATCH -e logs/%x_%j.err # Standard err goes to this file
#SBATCH --no-requeue # No requeue if preempted

module load intel-mkl/23.0.0-fasrc01 gcc/12.2.0-fasrc01 openmpi/4.1.4-fasrc01 
source ~/.bashrc
micromamba activate flare-Apr2025

export LANG=en_US.utf8
export LC_ALL=en_US.utf8
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK  # num_OMP*MPI_thread = number of cores

# srun -n $SLURM_NTASKS --mpi=pmix /n/holystore01/LABS/kozinsky_lab/Lab/Software/VASP6.3-GNU/vasp.6.3.0/bin/vasp_std

python -u dft_enthalpy.py


