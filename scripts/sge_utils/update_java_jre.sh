#!/bin/bash
#
#$ -V
#$ -pe orte 16
#$ -M mhofree@ucsd.edu
#$ -m ea
#$ -q ngs.q
#$ -j y
#$ -N update-java

update-java-alternatives -s java-1.7.0-openjdk-amd64
