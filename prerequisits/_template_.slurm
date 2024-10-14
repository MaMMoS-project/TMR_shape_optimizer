#!/bin/bash
#SBATCH --partition=dissSims
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G		# MB
#SBATCH --time=10-12		# MINUTES, DAYS-HOURS
#
# GPU options
#SBATCH --gres=gpu:1		# request also one cpu per gpu
#SBATCH --constraint=nv12
#
# OPTIONAL
#SBATCH --export=NONE   # do not propagate environment variables from submit node to allocated node
#SBATCH --job-name="<description>"	# default is batch script name
#SBATCH --account=zmus		# if we ever define project accounts
# #SBATCH --nodelist=Gd			# request a specific node, only as many as in --nodes
# #SBATCH --exclude=Nd		# do not grant resouces on those nodes

# INFO:
# --constraint options for gpu: 
# "nvidia" use any kind of nvidia card 
# "amd" use only dysprosium (for small gpu jobs)
# request specific cards: "nvidia12gb", "nvidia16gb", "amd8gb"
# combine specific cards with "nvidia12gb|nvidia16gb" (equal to "nvidia") 
# 
# number of tets per gpu:
# AMD Radeon R9 390 8GB: < 10e6 tets 
# NVIDIA Tesla K40|K80 12GB: < 18e6 tets
# NVIDIA Tesla P100-PCIE 16GB: < 25e6 tets 
# NVIDIA Tesla V100-PCIE 32GB: < 50e6 tets 
#
# --export=NONE
# By default all environment variables of the shell invoking the sbatch command are propagated.
# This may cause unexpected behaviour as for example $HOME used in this script might be different 
# from the expected /home/<username>. Also consider $PATH, $OCL* or $CUDA* variables. I recommend
# to set --export=NONE to avoid the propagation.

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

