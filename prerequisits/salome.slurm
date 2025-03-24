#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=25G
#SBATCH --time=1-0
#SBATCH --export=NONE
#SBATCH --job-name="<description>"
#SBATCH --exclude=Ce,Nd,Eu,Pr
#SBATCH --mail-type=END

SALOME="/scandium/home/programs/UB22/SALOME-9.7.0-native-DB10-SRC/salome"
JOBID="$SLURM_JOB_ID"
SIM_DIR="$HOME/slurm-$JOBID"

echo "JOBNAME:" $SLURM_JOB_NAME
echo "PARTITION:" $SLURM_JOB_PARTITION
echo "SUBMIT HOST:" $SLURM_SUBMIT_HOST
echo "ALLOC. NODES:" $SLURMD_NODENAME
echo "SUBMIT DIR:" $SLURM_SUBMIT_DIR

# copy files if necessary
SIMDIR="$HOME/slurm-$SLURM_JOB_ID"
mkdir -p "$SIMDIR"
export TMPDIR="$SIMDIR/tmp"
mkdir -p "$TMPDIR"
echo "SIMDIR: $SIMDIR"
echo "TMPDIR: $TMPDIR"
mkdir -p /tmp/logs/$USER


# prepare
cd "$SIM_DIR"
echo "PWD:" $PWD
cp "$SLURM_SUBMIT_DIR"/step2_salome_macroFullLM_2nm.py .

# Optionally set a unique SALOME tmp directory to avoid leftover /tmp usage
#export SALOME_TMP_DIR="$SIM_DIR"/salome_tmp
#mkdir -p "$SALOME_TMP_DIR"

# Run SALOME in batch mode
echo "Running SALOME..."
"$SALOME" start --shutdown=1 -t step2_salome_macroFullLM_2nm.py

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
