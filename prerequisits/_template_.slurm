#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --mem-per-gpu=15G
#SBATCH --constraint=nv12
#SBATCH --time=1-0
#SBATCH --export=NONE
#SBATCH --job-name="<description>"
#SBATCH --mail-type=END




MODELNAME="<model>"
# BINDIR="/ceph/programs/b4vex"
# MUMAGDIR="/ceph/share/users/fischbacher/bin/py"
# ESCRIPT="/ceph/programs/escript_py2/bin/run-escript"

export MAMBA_ROOT_PREFIX='/scandium/home/programs/micromamba/micromamba'
MAMBA_EXE='/scandium/home/programs/micromamba/bin/micromamba'
PROGRAMS='/scandium/home/programs'


echo "JOBNAME:" $SLURM_JOB_NAME
echo "PARTITION:" $SLURM_JOB_PARTITION
echo "SUBMIT HOST:" $SLURM_SUBMIT_HOST
echo "ALLOC. NODES:" $SLURMD_NODENAME
echo "SUBMIT DIR:" $SLURM_SUBMIT_DIR
# echo "MUMAG DIR:" $MUMAGDIR

# copy files if necessary
SIMDIR="$HOME"/slurm_"$SLURM_JOB_ID"
echo "SIMDIR:" $SIMDIR
if [ ! -d "$SIMDIR" ]; then
  mkdir -p "$SIMDIR"
fi
cp "$SLURM_SUBMIT_DIR"/"$MODELNAME".fly "$SIMDIR"
cp "$SLURM_SUBMIT_DIR"/"$MODELNAME".krn "$SIMDIR"
cp "$SLURM_SUBMIT_DIR"/"$MODELNAME".p2 "$SIMDIR"
cd "$SIMDIR"
echo "PWD:" $PWD

# simulation steps
export OCL_TYPE=GPU

$MAMBA_EXE run -n escript-python2 $PROGRAMS/escript_python2/bin/run-escript $PROGRAMS/b4vex/py/loop.py "$MODELNAME"
#$ESCRIPT "$MUMAGDIR"/loop.py "$MODELNAME"
head -n2 "$MODELNAME".anisotropy.mtx
wc -l "$MODELNAME".anisotropy.mtx

# "$BINDIR"/b4vex10restart "$MODELNAME"
$PROGRAMS/b4vex/b4vex10restart "$MODELNAME" 0

sleep 10

# clean up
rm "$MODELNAME".*.mtx
rm "$MODELNAME".fly
rm "$MODELNAME".hext.txt "$MODELNAME".loop.txt "$MODELNAME".meas.txt
rm "$MODELNAME".m.txt "$MODELNAME".x.txt "$MODELNAME".y.txt
#rm "$MODELNAME".dom.nc "$MODELNAME".m.????.txt

# Copy files back if necessary
if [[ "$SIMDIR" != "$SLURM_SUBMIT_DIR" ]]; then
  OUTPUTDIR="$SLURM_SUBMIT_DIR/output"  # Fixed the space before '='
  mkdir -p "$OUTPUTDIR"  # Use -p to avoid errors if the directory exists
  cp -r "$SIMDIR" "$OUTPUTDIR"
  cd ..
  rm -r "$SIMDIR"
fi

