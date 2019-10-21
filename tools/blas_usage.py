#!/usr/bin/env python

#   perf-libs-tools
#   Copyright 2017 Arm Limited. 
#   All rights reserved.

# Note we have the following stems
# BLAS1="rotg_ rotmg_ rot_ rotm_ swap_ scal_ copy_ axpy_ dot_ dotu_ dotc_ nrm2_ asum_ amax_"
# BLAS2="gemv_ gbmv_ hemv_ hbmv_ hpmv_ symv_ sbmv_ spmv_ trmv_ tbmv_ tpmv_ trsv_ tbsv_ tpsv_ ger_ geru_ gerc_ her_ hpr_ her2_ hpr2_ syr_ spr_ syr2_ spr2_"
# BLAS3="gemm_ symm_ hemm_ syrk_ herk_ syr2k_ her2k_ trmm_ trsm_"


import matplotlib.pyplot as plt
import numpy as np
import pylab
import math

import argparse		# Commandline argument parsing
#import os		# File directory structure parsing
#import json		# Needed for JSON input/output
#import time		# Used for getting the current date/time

import matplotlib

from matplotlib.patches import Shadow
from matplotlib import gridspec

BLAS1=["rotg_", "rotmg_", "rot_", "rotm_", "swap_", "scal_", "copy_", "axpy_", "dot_", "dotu_", "dotc_", "nrm2_", "asum_", "amax_"]
BLAS2=["gemv_", "gbmv_", "hemv_", "hbmv_", "hpmv_", "symv_", "sbmv_", "spmv_", "trmv_", "tbmv_", "tpmv_", "trsv_", "tbsv_", "tpsv_", "ger_", "geru_", "gerc_", "her_", "hpr_", "her2_", "hpr2_", "syr_", "spr_", "syr2_", "spr2_"]
BLAS3=["gemm_", "symm_", "hemm_", "syrk_", "herk_", "syr2k_", "her2k_", "trmm_", "trsm_"]


def parse_options():

# Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--legend", help="Show graph legend", dest='showLegend', default=False, action='store_true')
    parser.add_argument("-n", "--normalize", help="Normalize bars to percentages of max", dest='normalizeBars', default=False, action='store_true')
    parser.add_argument("-x", "--exclude", help="Exclude unrepresented functions", dest='excludeZeroes', default=False, action='store_true')
    parser.add_argument("-i", "--input", help="Input file", dest='inFile', default='')

    # Parse arguments
    args = parser.parse_args()
    return args



def main(args=None):
    print 'BLAS routine usage'
    args = parse_options()

    generate_blasplot(args)

def generate_blasplot(args):
    if (args.inFile) :
        data = np.loadtxt(args.inFile)
    else :
        print 'Showing example data.  Use "-i" option to select your own input.'
        data = np.loadtxt('tools/EXAMPLES/armpl-example.blas')

    cnt = 0
    b1z_its = []
    b1c_its = []
    b1d_its = []
    b1s_its = []
    b1z_time = []
    b1c_time = []
    b1d_time = []
    b1s_time = []
    b2z_its = []
    b2c_its = []
    b2d_its = []
    b2s_its = []
    b2z_time = []
    b2c_time = []
    b2d_time = []
    b2s_time = []
    b3z_its = []
    b3c_its = []
    b3d_its = []
    b3s_its = []
    b3z_time = []
    b3c_time = []
    b3d_time = []
    b3s_time = []
    removalList = []

    for routine in BLAS1 :
#        print routine, data[cnt], data[cnt+2], data[cnt+4], data[cnt+6]
        if (args.excludeZeroes) :
            zeroCnt = sum(data[cnt:cnt+7:2])
            if (zeroCnt < 1) :
                removalList.append(routine)
#                print 'removing routine ', routine
                cnt = cnt  + 8
                continue
#        print 'keeping routine ', routine, zeroCnt
        b1s_its.append(data[cnt])
        b1s_time.append(data[cnt+1])
        b1d_its.append(data[cnt+2])
        b1d_time.append(data[cnt+3])
        b1c_its.append(data[cnt+4])
        b1c_time.append(data[cnt+5])
        b1z_its.append(data[cnt+6])
        b1z_time.append(data[cnt+7])
            
        cnt = cnt  + 8
  
    if (args.excludeZeroes) :
        for routine in removalList :
            BLAS1.remove(routine)
        removalList = []

    for routine in BLAS2 :
#        print routine, data[cnt], data[cnt+2], data[cnt+4], data[cnt+6]
        if (args.excludeZeroes) :
            zeroCnt = sum(data[cnt:cnt+7:2])
            if (zeroCnt < 1) :
                removalList.append(routine)
#                print 'removing routine ', routine
                cnt = cnt  + 8
                continue
        b2s_its.append(data[cnt])
        b2s_time.append(data[cnt+1])
        b2d_its.append(data[cnt+2])
        b2d_time.append(data[cnt+3])
        b2c_its.append(data[cnt+4])
        b2c_time.append(data[cnt+5])
        b2z_its.append(data[cnt+6])
        b2z_time.append(data[cnt+7])
        cnt = cnt  + 8

    if (args.excludeZeroes) :
        for routine in removalList :
            BLAS2.remove(routine)
        removalList = []

    for routine in BLAS3 :
#        print routine, data[cnt], data[cnt+2], data[cnt+4], data[cnt+6]
        if (args.excludeZeroes) :
            zeroCnt = sum(data[cnt:cnt+7:2])
            if (zeroCnt < 1) :
                removalList.append(routine)
#                print 'removing routine ', routine
                cnt = cnt  + 8
                continue
        b3s_its.append(data[cnt])
        b3s_time.append(data[cnt+1])
        b3d_its.append(data[cnt+2])
        b3d_time.append(data[cnt+3])
        b3c_its.append(data[cnt+4])
        b3c_time.append(data[cnt+5])
        b3z_its.append(data[cnt+6])
        b3z_time.append(data[cnt+7])
        cnt = cnt  + 8
        
    if (args.excludeZeroes) :
        for routine in removalList :
            BLAS3.remove(routine)
        removalList = []
        
    maxval = 0.0
    maxvalt = 0.0
    if (len(b1s_its) > 0) :
        maxval = max(max(b1s_its), max(b1d_its), max(b1c_its), max(b1z_its))
        maxvalt = max(max(b1s_time), max(b1d_time), max(b1c_time), max(b1z_time))
    if (len(b2s_its) > 0) :
        maxval = max(max(b2s_its), max(b2d_its), max(b2c_its), max(b2z_its), maxval)
        maxvalt = max(max(b2s_time), max(b2d_time), max(b2c_time), max(b2z_time), maxvalt)
    if (len(b3s_its) > 0) :
        maxval = max(max(b3s_its), max(b3d_its), max(b3c_its), max(b3z_its), maxval)
        maxvalt = max(max(b3s_time), max(b3d_time), max(b3c_time), max(b3z_time), maxvalt)
#    print maxval, maxvalt

    

    if (args.normalizeBars) :
        b1s_its = [x*100/maxval for x in b1s_its]
        b1d_its = [x*100/maxval for x in b1d_its]
        b1c_its = [x*100/maxval for x in b1c_its]
        b1z_its = [x*100/maxval for x in b1z_its]
        b2s_its = [x*100/maxval for x in b2s_its]
        b2d_its = [x*100/maxval for x in b2d_its]
        b2c_its = [x*100/maxval for x in b2c_its]
        b2z_its = [x*100/maxval for x in b2z_its]
        b3s_its = [x*100/maxval for x in b3s_its]
        b3d_its = [x*100/maxval for x in b3d_its]
        b3c_its = [x*100/maxval for x in b3c_its]
        b3z_its = [x*100/maxval for x in b3z_its]
        b1s_time = [x*100.0/maxvalt for x in b1s_time]
        b1d_time = [x*100.0/maxvalt for x in b1d_time]
        b1c_time = [x*100.0/maxvalt for x in b1c_time]
        b1z_time = [x*100.0/maxvalt for x in b1z_time]
        b2s_time = [x*100.0/maxvalt for x in b2s_time]
        b2d_time = [x*100.0/maxvalt for x in b2d_time]
        b2c_time = [x*100.0/maxvalt for x in b2c_time]
        b2z_time = [x*100.0/maxvalt for x in b2z_time]
        b3s_time = [x*100.0/maxvalt for x in b3s_time]
        b3d_time = [x*100.0/maxvalt for x in b3d_time]
        b3c_time = [x*100.0/maxvalt for x in b3c_time]
        b3z_time = [x*100.0/maxvalt for x in b3z_time]

    
#    fig, ax = plt.subplots()
#    ax = plt.subplots()
    index1 = np.arange(len(BLAS1))
    index2 = np.arange(len(BLAS2))
    index3 = np.arange(len(BLAS3))
    bar_width = 0.25
    opacity = 0.8
    
    fig = plt.figure()
    fig.canvas.set_window_title('BLAS function usage - %s' % args.inFile) 
    plt.subplot(611)
    
#    print len(BLAS1), len(b1s_its)
#    print b1s_its
    
    plot1S = plt.bar(index1, b1s_its, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot1D = plt.bar(index1+bar_width, b1d_its, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot1C = plt.bar(index1+2*bar_width, b1c_its, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot1Z = plt.bar(index1+3*bar_width, b1z_its, bar_width,        alpha=opacity, color='g',        label="Z"    )

#    plt.xlabel('Routine')
    plt.ylabel('Iterations')
#    plt.title('BLAS level 1')
    #plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.xticks(index1 + bar_width, BLAS1)
#    plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
    if (args.showLegend and len(b1s_its)+len(b1d_its)+len(b1c_its)+len(b1z_its)>0) : 
        plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
        args.showLegend=0

#    print len(BLAS1), len(b1s_its)
    
#    plt.tight_layout()
#    plt.show()
    
    plt.subplot(612)
        
    #plt.ylim(ymin=0)
    plot2S = plt.bar(index2, b2s_its, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot2D = plt.bar(index2+bar_width, b2d_its, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot2C = plt.bar(index2+2*bar_width, b2c_its, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot2Z = plt.bar(index2+3*bar_width, b2z_its, bar_width,        alpha=opacity, color='g',        label="Z"    )
    
#    plt.xlabel('Routine')
    plt.ylabel('Iterations')
#    plt.title('BLAS level 2')
    plt.xticks(index2 + bar_width, BLAS2)
#    plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
    if (args.showLegend and len(b2s_its)+len(b2d_its)+len(b2c_its)+len(b2z_its)>0) : 
        plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
        args.showLegend=0

#    plt.tight_layout()
#    plt.show()
#    print len(BLAS3), len(b3s_its)

    plt.subplot(613)
        
    #plt.ylim(ymin=0)
    plot3S = plt.bar(index3, b3s_its, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot3D = plt.bar(index3+bar_width, b3d_its, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot3C = plt.bar(index3+2*bar_width, b3c_its, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot3Z = plt.bar(index3+3*bar_width, b3z_its, bar_width,        alpha=opacity, color='g',        label="Z"    )
    
#    plt.xlabel('Routine')
    plt.ylabel('Iterations')
#    plt.title('BLAS level 3')
    plt.xticks(index3 + bar_width, BLAS3)
#    plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
    if (args.showLegend and len(b3s_its)+len(b3d_its)+len(b3c_its)+len(b3z_its)>0) : 
        plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
        args.showLegend=0

#    plt.tight_layout()
    
    plt.subplot(614)
        
    #plt.ylim(ymin=0)
    plot1S = plt.bar(index1, b1s_time, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot1D = plt.bar(index1+bar_width, b1d_time, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot1C = plt.bar(index1+2*bar_width, b1c_time, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot1Z = plt.bar(index1+3*bar_width, b1z_time, bar_width,        alpha=opacity, color='g',        label="Z"    )

#    plt.xlabel('Routine')
    plt.ylabel('Time')
#    plt.title('BLAS level 1')
    plt.xticks(index1 + bar_width, BLAS1)
#    plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")

#    print len(BLAS1), len(b1s_time)
    
#    plt.tight_layout()
#    plt.show()
    
    plt.subplot(615)
        
    #plt.ylim(ymin=0)
    plot2S = plt.bar(index2, b2s_time, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot2D = plt.bar(index2+bar_width, b2d_time, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot2C = plt.bar(index2+2*bar_width, b2c_time, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot2Z = plt.bar(index2+3*bar_width, b2z_time, bar_width,        alpha=opacity, color='g',        label="Z"    )
    
#    plt.xlabel('Routine')
    plt.ylabel('Time')
#    plt.title('BLAS level 2')
    plt.xticks(index2 + bar_width, BLAS2)
#    plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")

#    plt.tight_layout()
#    plt.show()
#    print len(BLAS3), len(b3s_time)

    plt.subplot(616)
        
    #plt.ylim(ymin=0)
    plot3S = plt.bar(index3, b3s_time, bar_width,        alpha=opacity, color='r',        label="S"    )
    plot3D = plt.bar(index3+bar_width, b3d_time, bar_width,        alpha=opacity, color='b',        label="D"    )
    plot3C = plt.bar(index3+2*bar_width, b3c_time, bar_width,        alpha=opacity, color='y',        label="C"    )
    plot3Z = plt.bar(index3+3*bar_width, b3z_time, bar_width,        alpha=opacity, color='g',        label="Z"    )
    
#    plt.xlabel('Routine')
    plt.ylabel('Time')
#    plt.title('BLAS level 3')
    plt.xticks(index3 + bar_width, BLAS3)
    plt.xlim(xmin=0)
#    plt.xlim(xmax=1)
#    if (args.showLegend) : 
#        plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")

#    plt.tight_layout()
    print 7
    plt.show()
    



# Footer for catching no main
if __name__ == '__main__':
    main()
    
