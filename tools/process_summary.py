#!/usr/bin/env python

#   perf-libs-tools
#   Copyright 2017-8 Arm Limited. 
#   All rights reserved.

import matplotlib.pyplot as plt
import numpy as np
import pylab
import math

import os		# File directory structure parsing
import json		# Needed for JSON input/output
import time		# Used for getting the current date/time
import sys


import matplotlib

from matplotlib.patches import Shadow

def main(args=None):
    print( 'Process full dataset for BLAS, LAPACK and FFT function usage.')

    process_components()

#################################################
# Collect all the data about FFT calls made
#################################################
# Parse the FFT related lines of the armplsummary_#####.apl files
# Each routine has its own inputs requiring different treatment
#
# Note for now we are choosing to trust that all FFT calls are only made from user-called invocations, hence not worry about the top level timing information

def logFFT(readline, fftNames, fftLens, fftCnts, fftHowmany, fftTimes, fftPlanPtrs, fftExecPtrs):

  indexStore=0
  fftHowmany_sing = 0

  # set up the bits from the read line
  routine = readline[1]
  cnt = int(readline[3])
  avgtime = float(readline[5])
  if (routine.endswith("fft1mx_")) :
    plan = int(readline[4+7])
    nFFTs = int(readline[4+9])
    fftLen = [int(readline[4+10])]
  elif (routine.endswith("fft1m_")) :
    plan = int(readline[4+7])
    nFFTs = int(readline[4+8])
    fftLen = [int(readline[4+9])]
  elif (routine.endswith("fft1dx_")) :
    plan = int(readline[4+7])
    nFFTs = int(1)
    fftLen = [int(readline[4+9])]
  elif (routine.endswith("fft1d_")) :
    plan = int(readline[4+7])
    nFFTs = int(1)
    fftLen = [int(readline[4+8])]
  elif (routine.endswith("fft3dx_")) :
    plan = int(readline[4+7])
    nFFTs = int(1)
    fftLen = [int(readline[4+12]),int(readline[4+10]),int(readline[4+11])]
  elif (routine=="csfft_" or routine=="scfft_") :
    plan = int(readline[4+7])
    if plan==100 :
      plan = 0
    nFFTs = int(1)
    fftLen = [int(readline[4+8])]
  elif (routine=="dzfft_" or routine=="zdfft_") :
    plan = int(readline[4+7])
    if plan==100 :
      plan = 0
    nFFTs = int(1)
    fftLen = [int(readline[4+8])]
  elif (routine=="fftw_plan_dft_1d" or routine=="fftwf_plan_dft_1d") :
    plan = int(0)
    nFFTs = int(1)
    fftLen = [int(readline[4+7])]
    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    fftHowmany_sing = 1
    indexStore=1
  elif (
        routine=="fftw_plan_dft" or routine=="fftw_plan_dft_c2r" or routine=="fftw_plan_dft_r2c" or 
        routine=="fftwf_plan_dft" or routine=="fftwf_plan_dft_c2r" or routine=="fftwf_plan_dft_r2c" 
        ) :
    plan = int(0)
    nFFTs = int(1)  #### implemented through howmany for fftw interface
    # Assume at least 1-d
    fftLen = [int(readline[4+8])]
    if (int(readline[4+7])>1) :
       for index in range(1,int(readline[4+7])) :
          fftLen.append(int(readline[4+7+index]))
    fftHowmany_sing = 1  # advance by the number of dimensions
    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    indexStore=1
  elif (
        routine=="fftw_plan_many_dft" or routine=="fftw_plan_many_dft_c2r" or routine=="fftw_plan_many_dft_r2c" or 
        routine=="dfftw_plan_many_dft" or routine=="dfftw_plan_many_dft_c2r" or routine=="dfftw_plan_many_dft_r2c" or 
        routine=="dfftw_plan_many_dft_" or routine=="dfftw_plan_many_dft_c2r_" or routine=="dfftw_plan_many_dft_r2c_" or 
        routine=="sfftw_plan_many_dft" or routine=="sfftw_plan_many_dft_c2r" or routine=="sfftw_plan_many_dft_r2c" or 
        routine=="sfftw_plan_many_dft_" or routine=="sfftw_plan_many_dft_c2r_" or routine=="sfftw_plan_many_dft_r2c_" or 
        routine=="fftwf_plan_many_dft" or routine=="fftwf_plan_many_dft_c2r" or routine=="fftwf_plan_many_dft_r2c") :
    plan = int(0)
    nFFTs = int(1)  #### implemented through howmany for fftw interface
    # Assume at least 1-d
    fftLen = [int(readline[4+8])]
    if (int(readline[4+7])>1) :
       for index in range(1,int(readline[4+7])) :
          fftLen.append(int(readline[4+7+index]))
    fftHowmany_sing = int(readline[4+8+int(readline[4+7])])  # advance by the number of dimensions
    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    indexStore=1
  elif (routine=="fftw_plan_dft_2d" or routine=="fftwf_plan_dft_2d" or routine=="dfftw_plan_dft_2d_" or routine=="sfftw_plan_dft_2d_") :
    plan = int(0)
    nFFTs = int(1)  #### implemented through howmany for fftw interface
    fftLen = [int(readline[4+7]),int(readline[4+8])]
    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    fftHowmany_sing = 1
    indexStore=1
  elif (routine=="fftw_plan_dft_3d" or routine=="fftwf_plan_dft_3d" or routine=="dfftw_plan_dft_3d_" or routine=="sfftw_plan_dft_3d_") :
    plan = int(0)
    nFFTs = int(1)  #### implemented through howmany for fftw interface
    fftLen = [int(readline[4+7]),int(readline[4+8]),int(readline[4+9])]
    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    fftHowmany_sing = 1
    indexStore=1
  elif (routine=="fftw_plan_guru_dft" or routine=="fftw_plan_guru_dft_r2c" or routine=="fftw_plan_guru_dft_c2r" or
        routine=="fftwf_plan_guru_dft" or routine=="fftwf_plan_guru_dft_r2c" or routine=="fftwf_plan_guru_dft_c2r"
        ) :
    plan = int(0)
    nFFTs = int(1)  #### implemented through howmany for fftw interface

    # Assume at least 1-d
    fftLen = [int(readline[4+8])]
    if (int(readline[4+7])>1) :
       for index in range(1,int(readline[4+7])) :
          fftLen.append(int(readline[4+7+index]))
    fftHowmany_dims = int(readline[4+8+int(readline[4+7])])  # advance by the number of dimensions
    fftHowmany_sing = int(readline[1+4+8+int(readline[4+7])])
    if (fftHowmany_dims>1) :
       for index in range(1,fftHowmany_dims) : 
          fftHowmany_sing = fftHowmany_sing * int(readline[index+4+8+int(readline[4+7])])

    fftPlanPtrs.append([int(readline[-1]),routine,[-1,-1,-1]])
    indexStore=1
  elif (
        routine=="fftw_execute_dft" or routine=="fftw_execute_dft_r2c" or routine=="fftw_execute_dft_c2r" or
        routine=="dfftw_execute_dft" or routine=="dfftw_execute_dft_r2c" or routine=="dfftw_execute_dft_c2r" or
        routine=="dfftw_execute_dft_" or routine=="dfftw_execute_dft_r2c_" or routine=="dfftw_execute_dft_c2r_" or
        routine=="sfftw_execute_dft" or routine=="sfftw_execute_dft_r2c" or routine=="sfftw_execute_dft_c2r" or
        routine=="sfftw_execute_dft_" or routine=="sfftw_execute_dft_r2c_" or routine=="sfftw_execute_dft_c2r_" or
        routine=="fftwf_execute" or routine=="fftwf_execute_dft" or routine=="fftwf_execute_dft_r2c" or routine=="fftwf_execute_dft_c2r" 
        ) :
    # add to list of executions for processing later, then return
    # note we can't do this yet as the plans may not have been previously in the file at this point
    fftExecPtrs.append([int(readline[4+7]),int(readline[3]),float(readline[5])])
    return
  elif (
        routine=="fftw_destroy_plan" or routine=="dfftw_destroy_plan" or routine=="fftw_cleanup" or
        routine=="fftwf_destroy_plan" or routine=="sfftw_destroy_plan" or routine=="fftwf_cleanup"
        ) :
    return
  else :
    print( "Not implemented FFT parsing for routine %s" % routine)
    return
  
  found = 0
  fndInd=-1
  fndLen=-1
  fndHowmany=-1
  
  for fnNum in range(0,len(fftNames)) : 
    if (routine==fftNames[fnNum]) :
      fndInd=fnNum
      found = 1
      # Now search over existing lengths
      foundlen=0
      for i in range (0, len(fftLens[fnNum])) :
        testlen = fftLens[fnNum][i] 
        if ( testlen == fftLen ) :
          fndLen=i
          if (plan==0) :
             fftCnts[fnNum][i][0] += cnt*nFFTs
             fftTimes[fnNum][i][0] += cnt*avgtime
          else :
             fftCnts[fnNum][i][1] += cnt*nFFTs
             fftTimes[fnNum][i][1] += cnt*avgtime
          
          foundhow=0
          for index in range(0,len(fftHowmany[fnNum][i])) :
             if ( fftHowmany_sing == fftHowmany[fnNum][i][index] ) :
                foundhow = 1
                fndHowmany = index
                if (plan==0) :
                   fftCnts[fnNum][i][2][index] += cnt*nFFTs
                   fftTimes[fnNum][i][2][index] += cnt*avgtime
                else :
                   fftCnts[fnNum][i][3][index] += cnt*nFFTs
                   fftTimes[fnNum][i][3][index] += cnt*avgtime
                break

          if (foundhow == 0) :
             fndHowmany = len(fftHowmany[fnNum][i])
             fftHowmany[fnNum][i].append(fftHowmany_sing)
             if (plan==0) :
                fftCnts[fnNum][i][2].append(cnt*nFFTs)     # Note each transform has many FFTs performed, typically
                fftTimes[fnNum][i][2].append(cnt*avgtime)
                fftCnts[fnNum][i][3].append(0)             # Note adding corresponding zero entries into execute array
                fftTimes[fnNum][i][3].append(0.0)
             else :
                fftCnts[fnNum][i][2].append(0)             # Note adding corresponding zero entries into plan array
                fftTimes[fnNum][i][2].append(0.0)
                fftCnts[fnNum][i][3].append(cnt*nFFTs)     # Note each transform has many FFTs performed, typically
                fftTimes[fnNum][i][3].append(cnt*avgtime)

          foundlen=1
          break
          
      if (foundlen==0) :
        fndLen=len(fftLens[fnNum])
        fftLens[fnNum].append(fftLen)
        fndHowmany = 0
        fftHowmany[fnNum].append([fftHowmany_sing])
        if (plan==0) :
           fftCnts[fnNum].append([cnt*nFFTs, 0, [cnt*nFFTs], [0] ])     # Note each transform has many FFTs performed, typically
           fftTimes[fnNum].append([cnt*avgtime, 0.0, [cnt*avgtime], [0.0] ])
        else :
           fftCnts[fnNum].append([0, cnt*nFFTs, [0], [cnt*nFFTs] ])     # Note each transform has many FFTs performed, typically
           fftTimes[fnNum].append([0.0, cnt*avgtime, [0.0], [cnt*avgtime]])
      break

  if (found == 0) :
    fndInd = len(fftNames)  # remember we're adding 1 entry in a moment
    
    fftNames.append(routine)
    fftLens.append([fftLen])
    fftHowmany.append([[fftHowmany_sing]])
    fndLen=0
    fndHowmany=0
    if (plan==0) :
       fftCnts.append([[cnt*nFFTs, 0, [cnt*nFFTs], [0] ]])     # Note each transform has many FFTs performed, typically
       fftTimes.append([[cnt*avgtime, 0.0, [cnt*avgtime], [0.0] ]])
    else :
       fftCnts.append([[0,cnt*nFFTs, [0], [cnt*nFFTs] ]])     # Note each transform has many FFTs performed, typically
       fftTimes.append([[0.0, cnt*avgtime, [0.0], [cnt*avgtime] ]])

  if (indexStore==1) :
    fftPlanPtrs[-1][2] = [fndInd,fndLen,fndHowmany]
    
#################################################
# After collecting all calls we can associate 
# FFT plans with their corresponding executes
#################################################

def processFFTexecutes(fftNames, fftLens, fftCnts, fftHowmany, fftTimes, fftPlanPtrs, fftExecPtrs):

  for i in range(0,len(fftExecPtrs)) :
     ptr = fftExecPtrs[i][0]
     foundIndex=-1
     for j in range(0,len(fftPlanPtrs)):
        if fftPlanPtrs[j][0] == ptr:
           foundIndex=j
           break
     if foundIndex==-1 :
        print( "Missing plan!")
        continue   
     cnt=fftExecPtrs[i][1]
     avgtime=fftExecPtrs[i][2]
     nFFTs=1
     fnNum=fftPlanPtrs[foundIndex][2][0]
     fnInd=fftPlanPtrs[foundIndex][2][1]
     fnHowmany=fftPlanPtrs[foundIndex][2][2]
     
     
     fftCnts[fnNum][fnInd][1] = fftCnts[fnNum][fnInd][1]+cnt*nFFTs
     fftTimes[fnNum][fnInd][1] = fftTimes[fnNum][fnInd][1]+cnt*avgtime

     fftCnts[fnNum][fnInd][3][fnHowmany] = fftCnts[fnNum][fnInd][3][fnHowmany]+cnt*nFFTs
     fftTimes[fnNum][fnInd][3][fnHowmany] = fftTimes[fnNum][fnInd][3][fnHowmany]+cnt*avgtime
           
#################################################
# Calculate the total counts of each length FFT
# accumulating the relevant details from all FFT 
# calls, irrespective of dimension
#################################################

def processMultidimFFTs(fftNames, fftLens, fftCnts, fftTimes, fftHowmany) :

# First find maximum length
  maxlen=0
  for i in range(0,len(fftNames)) :
     routine = fftNames[i]
     if ( not routine.startswith("fftw") and not routine.startswith("sfftw") and not  routine.startswith("dfftw")) :
        continue
     for j in range(0,len(fftLens[i])) :
        for k in range(0,len(fftLens[i][j])) :
           testlen = fftLens[i][j][k]
           if (testlen>maxlen) :
              maxlen=testlen

# Now iniialize array of zeroes up to maxlen
  fftTotCnt = [0] * (maxlen+2)
  
# Now loop over FFTW routines called accumulating multidimensional counts  
  for routineNum in range(0,len(fftNames)) :
     routine = fftNames[routineNum]
     if ( not routine.startswith("fftw") and not routine.startswith("sfftw") and not  routine.startswith("dfftw")) :
        continue
     elif (routine.endswith("plan_dft_1d")) :
        for lenindex in range (0,len(fftLens[routineNum])) :
           testlen = fftLens[routineNum][lenindex][0]
           for testhowmany in range (0, len(fftCnts[routineNum][lenindex][3])) :
              fftTotCnt[testlen] += fftCnts[routineNum][lenindex][3][testhowmany]*fftHowmany[routineNum][lenindex][testhowmany]

     elif (routine.endswith("plan_dft_2d")) :
        nDim = 2
        for lenindex in range (0,len(fftLens[routineNum])) :
           for testhowmany in range (0, len(fftCnts[routineNum][lenindex][3])) :
              calcFftContribs(nDim, fftTotCnt, fftCnts[routineNum][lenindex][3][testhowmany], fftLens[routineNum][lenindex], fftHowmany[routineNum][lenindex][testhowmany])

     elif (routine.endswith("plan_dft_3d")) :
        nDim = 3
        for lenindex in range (0,len(fftLens[routineNum])) :
           for testhowmany in range (0, len(fftCnts[routineNum][lenindex][3])) :
              calcFftContribs(nDim, fftTotCnt, fftCnts[routineNum][lenindex][3][testhowmany], fftLens[routineNum][lenindex], fftHowmany[routineNum][lenindex][testhowmany])

     elif (routine.endswith("_plan_many_dft") or routine.endswith("_plan_many_dft_r2c") or routine.endswith("_plan_many_dft_c2r")) :
        for lenindex in range (0,len(fftLens[routineNum])) :
           nDim = len(fftLens[routineNum][lenindex]) 
           for testhowmany in range (0, len(fftCnts[routineNum][lenindex][3])) :
              calcFftContribs(nDim, fftTotCnt, fftCnts[routineNum][lenindex][3][testhowmany], fftLens[routineNum][lenindex], fftHowmany[routineNum][lenindex][testhowmany])


  for i in range(0, maxlen+2) :
     if (fftTotCnt[i] > 0) :
        print( "Length= %6d  Total count= %12d " % (i, fftTotCnt[i]))

#################################################
# Calculate the total number of each transform 
# in a multidimensional FFT
#################################################

def calcFftContribs(nDim, fftTotCnt, fftCnt, fftLens, fftHowmany) :
# Note fftCnt is now a multiplicative factor for all additiions below
#      fftLens is a list of our array of dimensions
#
## How do we handle 3-d FFTs, for instance
# If the line reads "fftw_plan_dft_3d len= [n1, n2, n3]" then this contains:
#           n2 transforms of length n1
#         + n1 transforms of length n2
#    + (n1*n2) transforms of length n3
#[+ (n1*n2*n3) transforms of length n4...]
#
# Want to produce a list of the total number of invocations of each length
# 
#  dimProduct=1
#  if (N==1)
#  	fftTotCnt[n[0]] ++;
#  else {
#    fftTotCnt[n[0]] += n[1];
#    dimProduct=n[0];
#    for (i=1; i< N; i++)
#    {
#	fftTotCnt[n[i]] += dimProduct;	}
#	dimProduct *= n[i]
#    }						}
#  }						}

  dimProduct=1
  
  if (nDim==1) :
     fftTotCnt[fftLens[0]] += 1*fftCnt*fftHowmany
  else :
     fftTotCnt[fftLens[0]] += fftLens[1]*fftCnt*fftHowmany
     dimProduct=fftLens[0]
     for i in range(1,nDim) :
        fftTotCnt[fftLens[i]] += dimProduct*fftCnt*fftHowmany
        dimProduct *= fftLens[i]

#################################################
# Collect all the data about BLAS calls made
#################################################

def logBLAS(readline, blasNames, blasCnts, blasTimes, blasCnts_top, blasTimes_top):

  # set up the bits from the read line
  routine = readline[1]
  cnt = int(readline[3])
  avgtime = float(readline[5])
  cnt_top = int(readline[7])
  avgtime_top = float(readline[9])
  
  found = 0
  for fnNum in range(0,len(blasNames)) : 
    if (routine==blasNames[fnNum]) :
      found = 1
      blasCnts[fnNum] += cnt
      blasTimes[fnNum] += cnt*avgtime
      blasCnts_top[fnNum] += cnt_top
      blasTimes_top[fnNum] += cnt_top*avgtime_top
      break

  if (found == 0) :
    blasNames.append(routine)
    blasCnts.append(cnt)     
    blasTimes.append(cnt*avgtime)
    blasCnts_top.append(cnt_top)     
    blasTimes_top.append(cnt_top*avgtime_top)
    
#################################################
# Collect all the data about LAPACK calls made
#################################################

def logLAPACK(readline, lapackNames, lapackCnts, lapackTimes, lapackCnts_top, lapackTimes_top):

  # set up the bits from the read line
  routine = readline[1]
  cnt = int(readline[3])
  avgtime = float(readline[5])
  cnt_top = int(readline[7])
  avgtime_top = float(readline[9])
  
  found = 0
  for fnNum in range(0,len(lapackNames)) : 
    if (routine==lapackNames[fnNum]) :
      found = 1
      lapackCnts[fnNum] += cnt
      lapackTimes[fnNum] += cnt*avgtime
      lapackCnts_top[fnNum] += cnt_top
      lapackTimes_top[fnNum] += cnt_top*avgtime_top
      break

  if (found == 0) :
    lapackNames.append(routine)
    lapackCnts.append(cnt)     
    lapackTimes.append(cnt*avgtime)
    lapackCnts_top.append(cnt_top)     
    lapackTimes_top.append(cnt_top*avgtime_top)
    

#################################################

def process_components():
    
  # initialize variables
  # Five categories : 0 BLAS1, 1 BLAS2, 2 BLAS3, 3 LAPACK, 4 FFT
  cnt = [0, 0, 0, 0, 0]
  cnt_top = [0, 0, 0, 0, 0]
  tottime = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
  tottime_top = [ 0.0, 0.0, 0.0, 0.0, 0.0 ]
  datatype_cnt=[0, 0, 0, 0]
  datatype_time=[0.0,0.0,0.0,0.0]
  datatype_cnt_top=[0, 0, 0, 0]
  datatype_time_top=[0.0,0.0,0.0,0.0]
  lastroutine="NULL"
  lastcategory=-1
  datatype=-1
  total_run_time = 0.0
  
  fftNames = [  ]
  fftLens = [ ]
  fftCnts = [ ]
  fftTimes = [ ]
  fftHowmany = [ ]
  
  blasNames = [ [],[],[] ]
  blasCnts = [ [],[],[] ]
  blasTimes = [ [],[],[] ]
  blasCnts_top = [ [],[],[] ]
  blasTimes_top = [ [],[],[] ]
  
  lapackNames = [  ]
  lapackCnts = [ ]
  lapackTimes = [ ]
  lapackCnts_top = [ ]
  lapackTimes_top = [ ]
  
  BLAS_ROUTINES=[
  	["rotg_", "rotmg_", "rot_", "rotm_", "swap_", "scal_", "copy_", "axpy_", "dot_", "dotu_", "dotc_", "nrm2_", "asum_", "amax_"],
  	["gemv_", "gbmv_", "hemv_", "hbmv_", "hpmv_", "symv_", "sbmv_", "spmv_", "trmv_", "tbmv_", "tpmv_", "trsv_", "tbsv_", "tpsv_", "ger_", "geru_", "gerc_", "her_", "hpr_", "her2_", "hpr2_", "syr_", "spr_", "syr2_", "spr2_"],
  	["gemm_", "symm_", "hemm_", "syrk_", "herk_", "syr2k_", "her2k_", "trmm_", "trsm_"],
  	]

# open input/output files
  # count the arguments
  nArguments = len(sys.argv) - 1
  
  for position in range (1, nArguments+1) :

    # open file
    print( "Opening file %s" % sys.argv[position])
    if os.path.isfile(sys.argv[position]) and os.access(sys.argv[position], os.R_OK):
        inputfile = open(sys.argv[position])
    else :
        print( "File >>>%s<<< is not readable.  Skipping..." % sys.argv[position])
        continue
    
    # Plan pointers are on a per-process basis so should only be tracked within a file
    fftPlanPtrs = [ ]
    fftExecPtrs = [ ]
    
    # read file    
    for line in  inputfile:
      readline = line.split()
      routine = readline[1]
      newcnt = readline[3]
      newavgtime = readline[5]
      newcnt_top = readline[7]
      newavgtime_top = readline[9]
      
      # Now let's search for the different sets in turn
      category=-1
      
      # Start with this bein the main function
      if (routine == "main") :
        total_run_time = total_run_time + float(newavgtime)
        category = -2

      # Quick get-out if it is the same as the previous
      if (routine == lastroutine) :
        category=lastcategory
            
      # FFTs : does it have the string "fft" in the routine name?
      if (category == -1 or category==4) :
        if ( routine.find("fft") > -1 ) :
          category = 4
          logFFT(readline, fftNames, fftLens, fftCnts, fftHowmany, fftTimes, fftPlanPtrs, fftExecPtrs)
          
      # BLAS : does it end in the right string_?
      if (category == -1 ) :
        for level in range(0,3) :
           for testfn in BLAS_ROUTINES[level] :
             if ( routine.endswith(testfn) ) :
               category = level
      
      # BLAS : Let's process this data
      if (category==0 or category==1 or category==2) :
        logBLAS(readline, blasNames[category], blasCnts[category], blasTimes[category], blasCnts_top[category], blasTimes_top[category])

      # LAPACK : Whatever's left!
      if (category == -1 or category==3) :
        logLAPACK(readline, lapackNames, lapackCnts, lapackTimes, lapackCnts_top, lapackTimes_top)
        category=3

      # Find datatype (for most routines)
      if (routine[0]=='d') :
        datatype=0
      elif (routine[0]=='s') :
        datatype=1
      elif (routine[0]=='z') :
        datatype=2
      elif (routine[0]=='c') :
        datatype=3


      if (category>-1) :        
        # Store data in correct set
        cnt[category] = cnt[category]+int(newcnt)
        tottime[category] = tottime[category]+float(newcnt)*float(newavgtime)
        cnt_top[category] = cnt_top[category]+int(newcnt_top)
        tottime_top[category] = tottime_top[category]+float(newcnt_top)*float(newavgtime_top)
        if (datatype != -1) :
          datatype_cnt[datatype] = datatype_cnt[datatype]+int(newcnt)
          datatype_time[datatype] = datatype_time[datatype]+float(newcnt)*float(newavgtime)
          datatype_cnt_top[datatype] = datatype_cnt_top[datatype]+int(newcnt_top)
          datatype_time_top[datatype] = datatype_time_top[datatype]+float(newcnt_top)*float(newavgtime_top)
      
      # Store last routine done for easy assignment
      lastroutine=routine
      lastcategory=category
      
    processFFTexecutes(fftNames, fftLens, fftCnts, fftHowmany, fftTimes, fftPlanPtrs, fftExecPtrs)
  
  #####
  # Print library function data
  #####
  
  print( "BLAS level 1     : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (cnt[0], tottime[0], cnt_top[0], tottime_top[0]) )
  print( "BLAS level 2     : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (cnt[1], tottime[1], cnt_top[1], tottime_top[1]) )
  print( "BLAS level 3     : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (cnt[2], tottime[2], cnt_top[2], tottime_top[2]) )
  print( "LAPACK           : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (cnt[3], tottime[3], cnt_top[3], tottime_top[3]) )
  print( "FFT              : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (cnt[4], tottime[4], cnt_top[4], tottime_top[4]) )
  print( " ")
  print( "Double precision : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (datatype_cnt[0], datatype_time[0], datatype_cnt_top[0], datatype_time_top[0]))
  print( "Single precision : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (datatype_cnt[1], datatype_time[1], datatype_cnt_top[1], datatype_time_top[1]))
  print( "Double complex   : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (datatype_cnt[2], datatype_time[2], datatype_cnt_top[2], datatype_time_top[2]))
  print( "Single complex   : count %10s    total time %12.4f  user count %10s  user time %12.4f" % (datatype_cnt[3], datatype_time[3], datatype_cnt_top[3], datatype_time_top[3]))

  #####
  # Print FFT summary data if present
  #####

  if (len(fftNames)>0) :
    print( " ")
    print( "FFT cases:")
    print( "----------")
    print( " FFTW calls:")
  
    # Printing without howmany info
    for fnNum in range(0,len(fftNames)) :
       if (fftNames[fnNum].find("fftw") > -1) :
          # convert to a tuple for sorting
          unorderedTuple = zip(fftLens[fnNum], fftCnts[fnNum], fftTimes[fnNum], fftHowmany[fnNum])
          orderedTuple = sorted(unorderedTuple, key=lambda field: field[0])
          for i in range(0,len(fftLens[fnNum])) :
             print( "%25s len= %5s   plan-cnt= %10d   plan-Time= %12.6f exec-cnt= %10d   exec-Time= %12.6f" % (
                fftNames[fnNum], orderedTuple[i][0], orderedTuple[i][1][0], orderedTuple[i][2][0], 
                orderedTuple[i][1][1], orderedTuple[i][2][1]))

    print( " ...of which the breakdown by 'howmany' cases shows:")
    # Printing with howmany info
    for fnNum in range(0,len(fftNames)) :
       if (fftNames[fnNum].find("fftw") > -1) :
          # convert to a tuple for sorting
          unorderedTuple = zip(fftLens[fnNum], fftCnts[fnNum], fftTimes[fnNum], fftHowmany[fnNum])
          orderedTuple = sorted(unorderedTuple, key=lambda field: field[0])
          for i in range(0,len(fftLens[fnNum])) :
             for j in range(0,len(orderedTuple[i][3])) :
                avgtime=0.0
                if (orderedTuple[i][1][3][j]>0 and orderedTuple[i][3][j]>0) :   # Check non-zero entries for fftCnt and fftHowmany
                   avgtime=(orderedTuple[i][2][3][j]/(orderedTuple[i][1][3][j]*orderedTuple[i][3][j]))
                print( "%25s len= %5s howmany= %10d  plan-cnt= %10d   plan-Time= %12.6f exec-cnt= %10d   exec-Time= %12.6f   avg-time= %16.10f" % (
                    fftNames[fnNum], orderedTuple[i][0], orderedTuple[i][3][j], orderedTuple[i][1][2][j], orderedTuple[i][2][2][j], 
                    orderedTuple[i][1][3][j], orderedTuple[i][2][3][j], avgtime))

    # Printing without howmany info
    printedheader = 0
    for fnNum in range(0,len(fftNames)) :
       if (not fftNames[fnNum].startswith("fftw")) :
          # Do header printing if there will be some content
          if (printedheader == 0) :
             print( " Other calls:")
             printedheader = 1
          # convert to a tuple for sorting
          unorderedTuple = zip(fftLens[fnNum], fftCnts[fnNum], fftTimes[fnNum], fftHowmany[fnNum])
          orderedTuple = sorted(unorderedTuple, key=lambda field: field[0])
          for i in range(0,len(fftLens[fnNum])) :
             print( "%25s len= %5s   plan-cnt= %10d   plan-Time= %12.6f exec-cnt= %10d   exec-Time= %12.6f" % (
                fftNames[fnNum], orderedTuple[i][0], orderedTuple[i][1][0], orderedTuple[i][2][0], 
                orderedTuple[i][1][1], orderedTuple[i][2][1]))

  processMultidimFFTs(fftNames, fftLens, fftCnts, fftTimes, fftHowmany)
  
  #####
  # Print BLAS summary data if present
  #####

  if (len(blasNames[0])+len(blasNames[1])+len(blasNames[2])>0) :
    print( " ")
    print( "BLAS cases:")
    print( "----------")
  
    for category in range(0,3) :
       if (len(blasNames[category])>0) :
          print( "BLAS level %d:" % (int(category)+1))
          # convert to a tuple for sorting
          unorderedTuple = zip(blasNames[category], blasCnts[category], blasTimes[category], blasCnts_top[category], blasTimes_top[category])
          orderedTuple = sorted(unorderedTuple, key=lambda field: field[2], reverse=True)
          for i in range(0,len(blasNames[category])) :
             print( "%8s     cnt= %10d  totTime= %12.4f   called_tot= %10d  topTime= %12.4f    (%%age of runtime: %6.3f )" % (
                 orderedTuple[i][0], orderedTuple[i][1], orderedTuple[i][2], orderedTuple[i][3], orderedTuple[i][4], orderedTuple[i][4]/float(total_run_time)*100.0))
             
  #####
  # Print LAPACK summary data if present
  #####

  if (len(lapackNames)>0) :
    print( " ")
    print( "LAPACK cases:")
    print( "----------")
  
    # convert to a tuple for sorting
    unorderedTuple = zip(lapackNames, lapackCnts, lapackTimes, lapackCnts_top, lapackTimes_top)
    orderedTuple = sorted(unorderedTuple, key=lambda field: field[2], reverse=True)
    for i in range(0,len(lapackNames)) :
       print( "%8s     cnt= %10d  totTime= %12.4f called_tot= %10d  topTime= %12.4f    (%%age of runtime: %6.3f )" % (
          orderedTuple[i][0], orderedTuple[i][1], orderedTuple[i][2], orderedTuple[i][3], orderedTuple[i][4], orderedTuple[i][4]/float(total_run_time)*100.0))

  #####
  # Generate 'armpl.blas' file for visualization afterwards
  #####
  
  if (len(blasNames[0])+len(blasNames[1])+len(blasNames[2])>0) :
     fname = '/tmp/armpl.blas'
     outputfile = open(fname, 'w')

     types="sdcz"
     for level in range(0,3) :
        for blasfn in BLAS_ROUTINES[level] :
           for prefix in types:
              found=0
              for index in range(0, len(blasNames[level])) :
                 testroutine = blasNames[level][index]
                 if ( not testroutine.startswith(prefix) ) :
                    continue
                 if ( testroutine.endswith(blasfn) ) :
                    outputfile.write( "%d\n %12.6f \n" % (blasCnts[level][index], blasTimes[level][index])) 
                    found=1
                    break
              if (found==0) :
                 outputfile.write( "%d\n %3.1f \n" %(0, 0))
     
     print("Created %s \nVisualize using ./blas_usage.py -x -l -i %s" %(fname, fname)  )

#########################################
# Footer for catching no main
if __name__ == '__main__':
    main()
    
