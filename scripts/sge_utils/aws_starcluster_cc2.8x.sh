#!/bin/bash
#
#$ -V
#$ -pe orte 32
#$ -M mhofree@ucsd.edu
#$ -m ea
#$ -q ngs.q
#$ -j y
#$ -N setup_dir
#$ -t 1-2

#mkfs -t ext4 /dev/xvdaa
#mkdir -p /media/ephemeral0
#mount -t ext4 /dev/xvdaa /media/ephemeral0
#
RUNDIR="/mnt"
chown sgeadmin $RUNDIR

su sgeadmin <<'EOF'
RUNDIR="/mnt"
cd ~
mkdir -p "$RUNDIR"/projects/cancer_ngs
ln -s "$RUNDIR"/projects
ln -s /mnt/ngs_deploy/projects/cancer_ngs/external ~/projects/cancer_ngs/external

#echo "export PATH=~/projects/cancer_ngs/external/tools/opt:~/projects/cancer_ngs/external/tools/bin:~/projects/cancer_ngs/external/bcbio-nextgen/anaconda/bin:$PATH" >> ~/.bashrc
#echo "export LD_LIBRARY_PATH=~/projects/cancer_ngs/external/tools/Cellar/bamtools/2.3.0/lib:~/projects/cancer_ngs/external/tools/Cellar/expat/2.1.0/lib:~/projects/cancer_ngs/external/tools/Cellar/gsl/1.16/lib:~/projects/cancer_ngs/external//tools/Cellar/htslib/0.2.0-rc5/lib:~/projects/cancer_ngs/external/tools/lib" >> ~/.bashrc
EOF
