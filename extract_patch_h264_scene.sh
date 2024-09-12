#!/bin/bash
#SBATCH -J vrr_patches
#SBATCH -A MANTIUK-SL3-CPU

#SBATCH -D /home/yl962/rds/hpc-work/VRR/VRRML_Create_Data
#SBATCH -o logs/vrr_patches/bistro/%a.log # TODO
#SBATCH -c 6
#SBATCH -t 01:00:00 # Time limit (hh:mm:ss)
#SBATCH -a 1

source $HOME/cvvdp_v2/bin/activate
module load ceuadmin/ffmpeg/5.1.1

scene="bistro" # TODO: change scene
echo "The current scene is: $scene"

echo "This task number $SLURM_ARRAY_TASK_ID"
echo "Using $SLURM_CPUS_PER_TASK CPUs cores"
echo

# Run the Python script
python extract_patch_h264_scene.py $SLURM_ARRAY_TASK_ID $scene