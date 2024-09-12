#!/bin/bash
#SBATCH -J vrr_patches
#SBATCH -A MANTIUK-SL3-CPU

#SBATCH -D /home/yl962/rds/hpc-work/VRR/VRRML_Create_Data
#SBATCH -o logs/vrr_patches/%a.log
# #SBATCH --mem=1G
#SBATCH -c 6
#SBATCH -t 01:00:00 # Time limit (hh:mm:ss)
#SBATCH -a 1

source $HOME/cvvdp_v2/bin/activate
module load ceuadmin/ffmpeg/5.1.1

echo "This task number $SLURM_ARRAY_TASK_ID"
echo "Using $SLURM_CPUS_PER_TASK CPUs cores"
echo

# Run the Python script
python extract_patch_h264.py $SLURM_ARRAY_TASK_ID