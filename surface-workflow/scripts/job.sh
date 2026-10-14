#!/bin/bash -l

#SBATCH --job-name=slab_convergence
#SBATCH --account=project_462001547
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=4
#SBATCH --mem=224G
#SBATCH --time=04:00:00
#SBATCH --output=slab_%j.out
#SBATCH --error=slab_%j.err

set -euo pipefail

# 1. Load LUMI software environment
module purge
module load LUMI/25.03
module load partition/C

# Load CP2K (verify available version)
# 
module use /users/neffd/EasyBuild/modules/LUMI/25.03/partition/L
module load CP2K/2024.3-cpeGNU-25.03-CPU

# 2. Activate your Python environment
source /pfs/lustrep4/projappl/project_462001547/DAVID/software/containers/surface_workflow/setup.sh


# 3. Configure threading
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_PLACES=cores
export OMP_PROC_BIND=close

# 4. Move to project directory
cd /pfs/lustrep4/projappl/project_462001547/DAVID/software/surface-workflow/surface-workflow/ 
# 5. Check environment
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "MPI ranks: $SLURM_NTASKS"
echo "OpenMP threads: $OMP_NUM_THREADS"

which python
which cp2k.psmp

# 6. Run your Python workflow
python -m surface_workflow

echo "Workflow finished"

