#!/usr/bin/env python

#   perf-libs-tools
#   Copyright 2017 Arm Limited. 
#   All rights reserved.

import matplotlib.pyplot as plt
import numpy as np
import pylab
import math

import argparse		# Commandline argument parsing
import os		# File directory structure parsing
import json		# Needed for JSON input/output
import time		# Used for getting the current date/time

import matplotlib

from matplotlib.patches import Shadow

def parse_options():

# Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", dest='inFile', default='')
    parser.add_argument("-l", "--legend", help="Show graph legend", dest='showLegend', default=False, action='store_true')
#    parser.add_argument("-n", "--normalize", help="Normalize bars to percentages of max", dest='normalizeBars', default=False, action='store_true')
#    parser.add_argument("-x", "--exclude", help="Exclude unrepresented functions", dest='excludeZeroes', default=False, action='store_true')

    # Parse arguments
    args = parser.parse_args()
    return args


def main(args=None):
    print('DGEMM heatmap creation')
    args = parse_options()

    generate_heatmap(args)

def generate_heatmap(args):
    
# The data file is in the format 2 * (N cols x N rows of ints) 2 rows of 5 ints, padded to N with 0
# follwed by 2 * (N cols x N rows of floats)
    if (args.inFile) :
        a = np.loadtxt(args.inFile)
    else :
        print('Showing example data.  Use "-i" option to select your own input.')
        a = np.loadtxt('tools/EXAMPLES/armpl-example.dgemm')

    maxvala = a.max()
    ncols = a.shape[1]

    b = np.zeros_like(a)
    step1 = (2 * ncols) + 2
    step2 = (3 * ncols) + 2
    for i in range (0, ncols):
        for j in range (0, ncols):
            b[i][j] = a[i+step1][j]
            b[i+ncols][j] = a[i+step2][j]

    maxvalb = b.max()
    for i in range (0, ncols):
        for j in range (0, ncols):
            b[i][j] = b[i][j]/maxvalb*maxvala

    fig = plt.figure()
    fig.canvas.set_window_title('DGEMM heatmaps - %s' % args.inFile) 
    plt.subplot(231)
    plt.xlabel('K (10^x))')
    plt.ylabel('M (10^y))')
    plt.title("A-shape - count")
    plt.imshow(a[0:ncols], cmap='gist_heat', interpolation='nearest', origin='lower', extent=(0.0,ncols,0.0,ncols), aspect='equal')

    plt.subplot(232)
    plt.xlabel('N (10^x))')
    plt.ylabel('K (10^y))')
    plt.title("B-shape - count")
    plt.imshow(a[ncols:2*ncols], cmap='gist_heat', interpolation='nearest', origin='lower', extent=(0.0,ncols,0.0,ncols), aspect='equal')

    plt.subplot(234)
    plt.xlabel('K (10^x))')
    plt.ylabel('M (10^y))')
    plt.title("A-shape - time")
    plt.imshow(b[0:ncols], cmap='gist_heat', interpolation='nearest', origin='lower', extent=(0.0,ncols,0.0,ncols), aspect='equal')

    plt.subplot(235)
    plt.xlabel('N (10^x))')
    plt.ylabel('K (10^y))')
    plt.title("B-shape - time")
    plt.imshow(b[ncols:2*ncols], cmap='gist_heat', interpolation='nearest', origin='lower', extent=(0.0,ncols,0.0,ncols), aspect='equal')

    pt_tot = np.sum(a[0:ncols])
    ncols2 = 2 * ncols
    nn_tot = a[ncols2][0]/pt_tot*100.0
    nt_tot = a[ncols2][1]/pt_tot*100.0
    tn_tot = a[ncols2][2]/pt_tot*100.0
    tt_tot = a[ncols2][3]/pt_tot*100.0

    pt_t_tot = np.sum(b[0:ncols])

    nn_t_tot = a[ncols2+1][0]/maxvalb*maxvala/pt_t_tot*100.0
    nt_t_tot = a[ncols2+1][1]/maxvalb*maxvala/pt_t_tot*100.0
    tn_t_tot = a[ncols2+1][2]/maxvalb*maxvala/pt_t_tot*100.0
    tt_t_tot = a[ncols2+1][3]/maxvalb*maxvala/pt_t_tot*100.0

# make a square figure and axes
    labels = ['NN', 'NT', 'TN', 'TT']
    sizes = [nn_tot, nt_tot, tn_tot, tt_tot]
    sizes_t = [nn_t_tot, nt_t_tot, tn_t_tot, tt_t_tot]

    if (tt_tot == 0) :
        labels.pop(3)
        sizes.pop(3)
        sizes_t.pop(3)
    if (tn_tot == 0) :
        labels.pop(2)
        sizes.pop(2)
        sizes_t.pop(2)
    if (nt_tot == 0) :
        labels.pop(1)
        sizes.pop(1)
        sizes_t.pop(1)
    if (nn_tot == 0) :
        labels.pop(0)
        sizes.pop(0)
        sizes_t.pop(0)

    expl_arr = np.zeros_like(sizes)
    expl_arr = expl_arr + 0.05

    plt.subplot(233)
    plt.pie(sizes, explode=expl_arr, labels=labels, autopct='%1.0f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.subplot(236)
    plt.pie(sizes_t, explode=expl_arr, labels=labels, autopct='%1.0f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    print('Done!')

    plt.show(block=True)
    plt.figure(num='This is the title')


# Footer for catching no main
if __name__ == '__main__':
    main()
