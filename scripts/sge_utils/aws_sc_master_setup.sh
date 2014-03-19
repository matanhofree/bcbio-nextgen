su sgeadmin <<'EOF'

echo "export PATH=~/projects/cancer_ngs/external/tools/opt:~/projects/cancer_ngs/external/tools/bin:~/projects/cancer_ngs/external/bcbio-nextgen/anaconda/bin:$PATH" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=~/projects/cancer_ngs/external/tools/Cellar/bamtools/2.3.0/lib:~/projects/cancer_ngs/external/tools/Cellar/expat/2.1.0/lib:~/projects/cancer_ngs/external/tools/Cellar/gsl/1.16/lib:~/projects/cancer_ngs/external//tools/Cellar/htslib/0.2.0-rc5/lib:~/projects/cancer_ngs/external/tools/lib" >> ~/.bashrc
EOF
