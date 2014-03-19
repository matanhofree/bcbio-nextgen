#!/usr/bin/env python -E
"""
A script to process CGHUB input to sample csv format.
Chooses samples according to the following set of rules:
1. Latest version.
2. Normal is chosen to match on the assembly, and be closest in date to the tumor.
3. Normal tumor is preferred to blood.  

Usage:
  generate_sample_file_fromcghub.py     
      -f sample file      
"""
import os
import sys
import string
import subprocess
import getopt
import datetime 
from collections import namedtuple
import pandas as pd

CGHUBFmt = namedtuple('CGHUBFmt','PID FILENAME FILEID DATE TYPE DISEASE')
cghubfmt = CGHUBFmt(1,13,16,24,4,2)

def usage():
    print ("generate_sample_file_fromcghub.py\n"     
           "    -s sample file\n")   
    
def extr_sample(samplefile):
    
    if (samplefile == '-'):
        with sys.stdin as f:
            sampleindex = f.readlines()
    else:        
        with open(samplefile) as f:
            sampleindex = f.readlines()
    
    extrDict = dict();    
             
    sampleData = pd.read_table(samplefile,sep='\t',compression="gzip", parse_dates=['uploaded'])        
    sampleData["PID"] = [ z[0:12] for z in sampleData["barcode"] ]  
 
    for pt in set(sampleData.ix[sampleData["sample_type"] == 'TP']["PID"]):
        tumorSet = sampleData.ix[map(all,zip(sampleData["sample_type"] == 'TP',  sampleData["PID"] == pt))]        
        ctumor = tumorSet.ix[tumorSet.uploaded.idxmax()]
        
        normalSet = sampleData.ix[map(all,zip(sampleData["sample_type"] != 'TP',  sampleData["PID"] == pt))]
        normalSet = normalSet.ix[normalSet.assembly == ctumor['assembly']]
        
        if len(normalSet) > 1:                  
            normalSet = normalSet.ix[(abs(normalSet.uploaded - ctumor["uploaded"])).idxmin()]                    
        elif len(normalSet) > 0:       
            normalSet = normalSet.iloc[0]                 
        else:
            continue; 
        
        extrDict[pt] = [ctumor['analysis_id'],normalSet['analysis_id'],ctumor["filename"],normalSet['filename'],ctumor['barcode'],normalSet['barcode']]      

    for key,val in extrDict.iteritems():
        print "%s,%s"%(key,",".join(val))    
                            

        
    
#     for cline in sampleindex:
#         sline = string.split(cline,"\t")                
#         if (sline[cghubfmt.TYPE] != 'TP'):
#             continue        
#         TCGAid = sline[cghubfmt.PID][0:12]
#         
#         if TCGAid not in sampleDict:
#             sampleDict[TCGAid] = sline
#         else:
#             sample_date =  datetime.datetime.strptime(sampleDict[TCGAid][cghubfmt.DATE], "%Y-%m-%d").date()
#             row_date = datetime.datetime.strptime(sline[cghubfmt.DATE], "%Y-%m-%d").date()
#             
#             if (sample_date < row_date):
#                 sampleDict[TCGAid] = sline
#                 
# #     for cline in sampleinex:
# #         sline = string.split(cline,"\t")
# #         if (sline[4] == 'TP'):
# #             continue
# #         TCGAid = sline[1][0:12]
#         
#     for key,val in sampleDict.iteritems():
#         print key,val                    
    
            
def main(argv): 
    outputdir = os.getcwd()     
    samplefile = '';
        
    try:
        opts, args = getopt.getopt(argv, "hs:", ["samplefile=" ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(1)   
        elif opt in ("-s", "--samplefile"):
            samplefile = arg       
        else:
            usage()
            sys.exit(3)
   
    print 'Output dir: ', outputdir
    print 'Sample file: ', samplefile    
    
    extr_sample(samplefile)


if __name__ == "__main__":
    main(sys.argv[1:])
