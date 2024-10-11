#!/bin/bash
#SBATCH --partition=dissSims
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G	# MB
#SBATCH --time=0-2		# MINUTES, DAYS-HOURS

#
# OPTIONAL
#SBATCH --export=None
#SBATCH --job-name="salome_equi_n128_dirac75_2nm"	# default is batch script name
# #SBATCH --account=zmus		# if we ever define project accounts
# #SBATCH --nodelist=Gd			# request a specific node, only as many as in --nodes
# #SBATCH --exclude=Eu,Ce,Y,Pr		# do not grant resouces on those nodes

SALOME="/scandium/home/programs/UB22/SALOME-9.7.0-native-DB10-SRC/salome"

echo "JOBNAME:" $SLURM_JOB_NAME
echo "PARTITION:" $SLURM_JOB_PARTITION
echo "SUBMIT HOST:" $SLURM_SUBMIT_HOST
echo "ALLOC. NODES:" $SLURMD_NODENAME
echo "SUBMIT DIR:" $SLURM_SUBMIT_DIR

# copy files if necessary
SIM_DIR="$HOME"/slurm-"$SLURM_JOB_ID"
echo "SIM_DIR:" $SIM_DIR
if [ ! -d "$SIM_DIR" ]; then
  mkdir -p "$SIM_DIR"
fi

# prepare
cd "$SIM_DIR"
echo "PWD:" $PWD
cp "$SLURM_SUBMIT_DIR"/step2_salome_macroFullLM_2nm.py .
#cp "$SLURM_SUBMIT_DIR"/equi_128_dirac75.tess .
#cp "$SLURM_SUBMIT_DIR"/c300_lnorm_50.00_21.00_1.00.tess .

# meshing
"$SALOME" start -t step2_salome_macroFullLM_2nm.py

sleep 10 

# copy files back if necessary
if [[ "$SIM_DIR" != "$SLURM_SUBMIT_DIR" ]]; then
  RESULT_DIR="$SLURM_SUBMIT_DIR"/results
  mkdir -p "$RESULT_DIR"
  cp -r "$SIM_DIR" "$RESULT_DIR"
  mv "$SLURM_SUBMIT_DIR"/slurm-"$SLURM_JOB_ID".out  "$RESULT_DIR"/slurm-"$SLURM_JOB_ID"
  cd "$SLURM_SUBMIT_DIR"
  rm -r "$SIM_DIR"
  #  cp -r "$SIM_DIR"/. "$SLURM_SUBMIT_DIR"/
#  rm -r "$SIM_DIR"
fi
