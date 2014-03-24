#!/usr/bin/env python -E
"""
Run an automated analysis pipeline for high throughput sequencing data.
Input: 
    sample_file
    index - 
Process:
1. Use gtdownload to download input bam files 
2. Write a bcbio_nextgen.py yaml file based on template 
3.   

Usage:
  bcbio_ngs_tcga_batch.py 
      -k gtdownloand key file
      -o output directory
      -f sample file
      -i index number
"""
import os
import sys
import string
import subprocess
import getopt
import datetime
from bcbio.pipeline.main import run_main, parse_cl_args

def usage():
    print ("bcbio_ngs_tcga_batch.py\n"
           "    -k gtdownloand key file\n"
           "    -o output directory\n"
           "    -s sample file\n"
           "    -i index file\n")
    
def fetch_cghub_file(keyFile,fID,sampleDir):
    fetchAddress = "https://cghub.ucsc.edu/cghub/data/analysis/download/"
    cghubRunCmd = "gtdownload -c {keyFile} -d https://cghub.ucsc.edu/cghub/data/analysis/download/{fID} -p {sampleDir} -v"
    cghubRunCmd = cghubRunCmd.format(**locals())
    print "Fetching from CGHUB:", cghubRunCmd
    retcode = subprocess.call(cghubRunCmd,shell=True) 
    return retcode   
    
def write_yaml(workDir,patientID,tumorFile,normalFile,tumorID,normalID):
    yamlTxt = \
"""
details:
- algorithm:
    aligner: bwa
    coverage_depth: high
    coverage_interval: exome
    mark_duplicates: picard
    platform: illumina
    quality_format: standard
    realign: gatk
    recalibrate: gatk
    variantcaller: [ mutect, varscan, freebayes ]
  analysis: variant2
  description: {tumorID}
  files: {tumorFile}
  genome_build: GRCh37
  metadata:
    batch: {patientID}
    phenotype: tumor
- algorithm:
    aligner: bwa
    coverage_depth: high
    coverage_interval: exome
    mark_duplicates: picard
    platform: illumina
    quality_format: standard
    realign: gatk
    recalibrate: gatk
    variantcaller: [ mutect, varscan, freebayes ]
  analysis: variant2
  description: {normalID}
  files: {normalFile}
  genome_build: GRCh37
  metadata:
    batch: {patientID}
    phenotype: normal
fc_date: {todaysDate}
fc_name: {patientID}_mutect
upload:
    dir: /mnt/result/{patientID}_final
    
"""

    zdate = datetime.date.today()
    todaysDate = zdate.strftime('%y%m%d')
    yamlTxt = yamlTxt.format(**locals())
    yamlPathName = "%s%s%s_runcfg.yaml"%(workDir,os.sep,patientID)
    
    with open(yamlPathName, "w") as yamlFH:
        yamlFH.write(yamlTxt)
        
    return yamlPathName
        
    
def run_ngs_align(configFile,workDir,coresN):
    os.chdir(workDir)
    
#     runcmd = "bcbio_nextgen.py {configFile} -n {coresN} -t local"
#     runcmd = runcmd.format(**locals())
#     print "Running:", runcmd
#    runval = subprocess.call(runcmd,shell=True,stdout = subprocess.PIPE, stderr= subprocess.PIPE)
#     runval = subprocess.call(runcmd,shell=True)

    run_param = [ configFile , '-t' ,'local' ,'-n', coresN ]
    kwargs = parse_cl_args(run_param)
    run_main(**kwargs)
    


def run_sample(outputdir,keyfile,samplefile,findex,ncores):
    
    if (os.path.isdir(outputdir) == False):
        print "Error: output dir does not exist"
        usage()        
        sys.exit(4)
    elif (os.path.isfile(keyfile) == False):
        print "Error: key file does not exist"
        usage()
        sys.exit(5)
    elif (os.path.isfile(samplefile) == False):
        print "Error: sample file does not exist"
        usage()
        sys.exit(6)
    
    with open(samplefile) as f:
        sampleindex = f.read().splitlines()
        
    if (findex < 0 or findex > len(sampleindex)):
        print "Error: sample index out of bounds"
        usage()
        sys.exit(7)
        
    fparam = string.split(sampleindex[findex],",")
    print 'Fetching the following ids from CGHub: "', fparam
    
    patientID = fparam[0]
    tumorID = fparam[1]
    normalID = fparam[2]
    tumorFileName = fparam[3]
    normalFileName = fparam[4]
    tumorTCGA = fparam[5]
    normalTCGA = fparam[6]
    
    workDir = outputdir + os.sep + patientID
    sampleDir = workDir + os.sep + 'inputData'
    configDir = workDir + os.sep + 'conf'
    sampleFileFullTumor = workDir + os.sep + 'inputData' + os.sep + tumorID + os.sep + tumorFileName
    sampleFileFullNormal = workDir + os.sep + 'inputData' + os.sep + normalID + os.sep + normalFileName
    
    if not os.path.exists(workDir):
        os.makedirs(workDir)  
        
    if not os.path.exists(workDir + os.sep + 'work'):
        os.makedirs(workDir + os.sep + 'work')      
    
    if not os.path.exists(sampleDir):
        os.makedirs(sampleDir)
    
    if not os.path.exists(configDir):
        os.makedirs(configDir)
    
    if (not os.path.isfile(sampleFileFullTumor)):    
        tumorRet = fetch_cghub_file(keyfile,tumorID,sampleDir)
        if ((tumorRet is not None) or (not os.path.isfile(sampleFileFullTumor))):
            print "Error: file download error:",tumorRet,sampleFileFullTumor
            sys.exit(11)
        
    if (not os.path.isfile(sampleFileFullNormal)):
        normalRet = fetch_cghub_file(keyfile,normalID,sampleDir)
        if ((normalRet is not None) or (not os.path.isfile(sampleFileFullNormal))):
            print "Error: file download error",normalRet,sampleFileFullNormal
            sys.exit(11)
           
    configFile = write_yaml(configDir,patientID,sampleFileFullTumor,sampleFileFullNormal,tumorTCGA,normalTCGA)   
    run_ngs_align(configFile,workDir + os.sep + 'work',ncores)                
    print 'Done: ', patientID      
            
def main(argv): 
    outputdir = os.getcwd() + '/results/' 
    findex = 0;
    samplefile = '';
    keyfile = ''; 
    ncores = '8'   
        
    try:
        opts, args = getopt.getopt(argv, "hi:o:s:k:n:", ["index=", "odir=", "samplefile=", "key=","ncores=" ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(1)
        elif opt in ("-i", "--index"):
            findex = int(arg)
        elif opt in ("-o", "--odir"):
            outputdir = arg
        elif opt in ("-s", "--samplefile"):
            samplefile = arg
        elif opt in ("-k", "--key"):
            keyfile = arg    
        elif opt in ("-n", "--ncores"):
            ncores = arg            
        else:
            usage()
            sys.exit(3)
   
    print 'Output dir: ', outputdir
    print 'Key file: ', keyfile
    print 'Sample file: ', samplefile
    print 'Sample index: ', findex
    
    run_sample(outputdir,keyfile,samplefile,findex,ncores)


if __name__ == "__main__":
    main(sys.argv[1:])
