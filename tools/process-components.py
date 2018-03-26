#!/usr/bin/env python

#   perf-libs-tools
#   Copyright 2017 Arm Limited. 
#   All rights reserved.

import matplotlib.pyplot as plt
import numpy as np
import pylab
import math

#import argparse		# Commandline argument parsing
import os		# File directory structure parsing
import json		# Needed for JSON input/output
import time		# Used for getting the current date/time
import sys


import matplotlib

from matplotlib.patches import Shadow

#def parse_options():
#
## Create argument parser
#    parser = argparse.ArgumentParser()
#    parser.add_argument("-i", "--input", help="Input file", dest='inFile', default='')
#    parser.add_argument("-l", "--legend", help="Show graph legend", dest='showLegend', default=False, action='store_true')
##    parser.add_argument("-n", "--normalize", help="Normalize bars to percentages of max", dest='normalizeBars', default=False, action='store_true')
##    parser.add_argument("-x", "--exclude", help="Exclude unrepresented functions", dest='excludeZeroes', default=False, action='store_true')
#
#    # Parse arguments
#    args = parser.parse_args()
#    return args


def main(args=None):
    print 'Process full dataset'
#    args = parse_options()

    process_components()

#################################################

def process_components():
    
  # initialize variables
  # Five categories : 0 BLAS1, 1 BLAS2, 2 BLAS3, 3 LAPACK, 4 FFT
  cnt = [0, 0, 0, 0, 0]
  tottime = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
  datatype_cnt=[0, 0, 0, 0]
  datatype_time=[0.0,0.0,0.0,0.0]
  lastroutine="NULL"
  lastcategory=-1
  datatype=-1
  
  BLAS1=["rotg_", "rotmg_", "rot_", "rotm_", "swap_", "scal_", "copy_", "axpy_", "dot_", "dotu_", "dotc_", "nrm2_", "asum_", "amax_"]
  BLAS2=["gemv_", "gbmv_", "hemv_", "hbmv_", "hpmv_", "symv_", "sbmv_", "spmv_", "trmv_", "tbmv_", "tpmv_", "trsv_", "tbsv_", "tpsv_", "ger_", "geru_", "gerc_", "her_", "hpr_", "her2_", "hpr2_", "syr_", "spr_", "syr2_", "spr2_"]
  BLAS3=["gemm_", "symm_", "hemm_", "syrk_", "herk_", "syr2k_", "her2k_", "trmm_", "trsm_"]
  

# open input/output files
  # count the arguments
  nArguments = len(sys.argv) - 1
  
  for position in range (1, nArguments+1) :

    # open file
    print "Opening file %s" % sys.argv[position]
    if os.path.isfile(sys.argv[position]) and os.access(sys.argv[position], os.R_OK):
        inputfile = open(sys.argv[position])
    else :
        print "File >>>%s<<< is not readable.  Skipping..." % sys.argv[position]
        continue
    
    # read file    
    for line in  inputfile:
      readline = line.split()
      routine = readline[1]
      newcnt = readline[3]
      newavgtime = readline[5]

      # Now let's search for the different sets in turn
      category=-1
      
      # Quick get-out if it is the same as the previous
      if (routine == lastroutine) :
        category=lastcategory
      
      # FFTs : does it have the string "fft" in the routine name?
      if (category == -1 ) :
        if ( routine.find("fft") > -1 ) :
          category = 4
      
      # BLAS 1 does it end in the right string_?
      if (category == -1 ) :
        for testfn in BLAS1 :
          if ( routine.endswith(testfn) ) :
            category = 0
      # BLAS 2 does it end in the right string_?
      if (category == -1 ) :
        for testfn in BLAS2 :
          if ( routine.endswith(testfn) ) :
            category = 1
      # BLAS 3 does it end in the right string_?
      if (category == -1 ) :
        for testfn in BLAS3 :
          if ( routine.endswith(testfn) ) :
            category = 2
      
      # LAPACK: Whatever's left!
      if (category == -1 ) :
        category=3
      
#      if (category==2) :
#            print routine, float(newcnt)*float(newavgtime), tottime[2]

      # Find datatype (for most routines)
      if (routine[0]=='d') :
        datatype=0
      elif (routine[0]=='s') :
        datatype=1
      elif (routine[0]=='z') :
        datatype=2
      elif (routine[0]=='c') :
        print routine
        datatype=3
        
      # Store data in correct set
      cnt[category] = cnt[category]+int(newcnt)
      tottime[category] = tottime[category]+float(newcnt)*float(newavgtime)
      if (datatype != -1) :
        datatype_cnt[datatype] = datatype_cnt[datatype]+int(newcnt)
        datatype_time[datatype] = datatype_time[datatype]+float(newcnt)*float(newavgtime)
      
      # Store last routine done for easy assignment
      lastroutine=routine
      lastcategory=category

  print "BLAS level 1     : count %8s    total time %12.4f" % (cnt[0], tottime[0]) 
  print "BLAS level 2     : count %8s    total time %12.4f" % (cnt[1], tottime[1]) 
  print "BLAS level 3     : count %8s    total time %12.4f" % (cnt[2], tottime[2]) 
  print "LAPACK           : count %8s    total time %12.4f" % (cnt[3], tottime[3]) 
  print "FFT              : count %8s    total time %12.4f" % (cnt[4], tottime[4]) 
  print " "
  print "Double precision : count %8s    total time %12.4f" % (datatype_cnt[0], datatype_time[0])
  print "Single precision : count %8s    total time %12.4f" % (datatype_cnt[1], datatype_time[1])
  print "Double complex   : count %8s    total time %12.4f" % (datatype_cnt[2], datatype_time[2])
  print "Single complex   : count %8s    total time %12.4f" % (datatype_cnt[3], datatype_time[3])

# Footer for catching no main
if __name__ == '__main__':
    main()
    
