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
import hashlib
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
    dir: /mnt/results/{patientID}_final
    
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
    


def run_sample(runSettings):
    
    outputdir = runSettings["outputdir"]
    keyfile = runSettings["keyfile"]
    samplefile = runSettings["samplefile"]
    findex = runSettings["findex"]
    ncores = runSettings["ncores"] 
    
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
    tumorMD5 = fparam[7]
    normalMD5 = fparam[8]
    
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
        
    # Download and check file
    download_file(sampleFileFullTumor,tumorID,sampleDir,tumorMD5,runSettings)
    download_file(sampleFileFullNormal,normalID,sampleDir,normalMD5,runSettings)
        
    configFile = write_yaml(configDir,patientID,sampleFileFullTumor,sampleFileFullNormal,tumorTCGA,normalTCGA)   
    run_ngs_align(configFile,workDir + os.sep + 'work',ncores)                
    print 'Done: ', patientID      
    
def download_file(sampleFile,fileID,sampleDir,fileMD5,runSettings):
    keyfile = runSettings["keyfile"]
    dlretry = runSettings["dlretry"]
    checkHash = runSettings["checkHash"] 
    hashPass = not(checkHash)

    # Download file if necessary
    for i in xrange(0,dlretry):
        if (not os.path.isfile(sampleFile)):            
            print "Downloading file from CGhub: %s (attempt %d)" % (sampleFile,i)
            
            fileRet = fetch_cghub_file(keyfile,fileID,sampleDir)                                
            if ((fileRet != 0 ) or (not os.path.isfile(sampleFile))):
                print "Error: file download error:",fileRet,sampleFile
        
        if (hashPass == False): # Test hash value
            # Test checksum
            with open(sampleFile,'rb') as fileCheck:
                # read contents of the file                  
                md5_returned = hashfile(fileCheck, hashlib.md5())
                
            if (md5_returned != fileMD5):
                print "Failed md5 checksum failed: %s %s %s" % (sampleFile, md5_returned, fileMD5)                
            else:
                print "MD5 checksum passed"
                hashPass = True
                break
                    
        # Try to download again
        fileRet = fetch_cghub_file(keyfile,fileID,sampleDir)                                
        if ((fileRet != 0 ) or (not os.path.isfile(sampleFile))):
            print "Error: file download error:",fileRet,sampleFile
            
                

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()
            
def main(argv): 
    
    runSettings = dict()        
    runSettings["outputdir"] = os.getcwd() + '/results/' 
    runSettings["findex"] = 0
    runSettings["samplefile"] = ''
    runSettings["keyfile"] = '' 
    runSettings["ncores"] = '32'
    runSettings["dlretry"] = 3
    runSettings["emailOnErr"] = True     
    runSettings["checkHash"] = True
        
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
            runSettings["findex"] = int(arg)
        elif opt in ("-o", "--odir"):
            runSettings["outputdir"] = arg
        elif opt in ("-s", "--samplefile"):
            runSettings["samplefile"] = arg
        elif opt in ("-k", "--key"):
            runSettings["keyfile"] = arg    
        elif opt in ("-n", "--ncores"):
            runSettings["ncores"] = arg            
        else:
            usage()
            sys.exit(3)
   
    print 'Output dir: ', runSettings["outputdir"]
    print 'Key file: ', runSettings["keyfile"]
    print 'Sample file: ', runSettings["samplefile"]
    print 'Sample index: ', runSettings["findex"]
    
    try:
        run_sample(runSettings)
    except:
        err = sys.exc_info()[0]
        print err        
        


if __name__ == "__main__":
    main(sys.argv[1:])
