#!/usr/bin/env python


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
from matplotlib.ticker import ScalarFormatter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title", help="Title of Graph", dest='title', default='')
    parser.add_argument("-i", "--input", help="Input file", dest='inFile', default='')
    parser.add_argument("-o", "--output", help="Output file", dest='outFile', default=None)
    args = parser.parse_args()



    data = np.loadtxt(args.inFile)
    print("Unique DGEMM Calls ", data.shape[0])
    aggregated_mk = {}
    aggregated_kn = {}

    for entry in data:
        if (entry[0], entry[2]) in aggregated_mk:
            # print(entry[4] - aggregated_mk[(entry[0], entry[2])][1])
            aggregated_mk[(entry[0], entry[2])] =  (aggregated_mk[(entry[0], entry[2])][0] + entry[3], aggregated_mk[(entry[0], entry[2])][1] + entry[3]*entry[4])
        else:
            aggregated_mk[(entry[0], entry[2])] = (entry[3], entry[4])

        if (entry[2], entry[1]) in aggregated_kn:
            aggregated_kn[(entry[2], entry[1])] = (aggregated_kn[(entry[2], entry[1])][0] + entry[3], aggregated_kn[(entry[2], entry[1])][1] + entry[3]*entry[4])
        else:
            aggregated_kn[(entry[2], entry[1])] = (entry[3], entry[4])



    # print("MK Counts ", len(aggregated_mk))    
    # print("MK Counts ", aggregated_mk)
    # print("KN Counts ", len(aggregated_kn))    
    # print("KN Counts ", aggregated_kn)
    



    colors = np.random.rand(data.shape[0])
    area_mod = (35**2)

    fig = plt.figure()
    fig.suptitle(args.title, fontsize="x-large")
    fig.set_figheight(6)
    fig.set_figwidth(14)
    fig.set_figheight(12)
    fig.set_figwidth(14)
    plt.subplots_adjust(hspace=0.4,wspace=0.4)
    fig.canvas.set_window_title('DGEMM Hotspots')

    # fig, ax = plt.subplots()
    # for axis in [ax.xaxis, ax.yaxis]:
    #     axis.set_major_formatter(ScalarFormatter())


    plt.subplot(221)
    plt.xlabel('K')
    plt.ylabel('M')
    plt.title("A-Matrix Shape: Count")
    xs, ys, vals = [], [], []
    for key in aggregated_mk:
        ys.append(key[0])
        xs.append(key[1])
        vals.append(aggregated_mk[key][0])
    print(max(vals), sum(vals))
    plt.scatter(xs, ys, s=[(x/30000.0)*area_mod for x in vals], c='c', alpha=0.5)
    plt.xscale("log")
    plt.yscale("log")
    # plt.xlim(0, np.max(data[:0]))
    # plt.ylim(0, np.max(data[:2]))
    plt.xlim(0, 100000)
    plt.ylim(0, 100000)

    plt.subplot(222)
    plt.xlabel('N')
    plt.ylabel('K')
    plt.title("B-Matrix Shape: Count")
    xs, ys, vals = [], [], []
    for key in aggregated_kn:
        ys.append(key[0])
        xs.append(key[1])
        vals.append(aggregated_kn[key][0])
    print(max(vals), sum(vals))
    plt.scatter(xs, ys, s=[(x/30000.0)*area_mod for x in vals], c='c', alpha=0.5)
    plt.xscale("log")
    plt.yscale("log")
    # plt.xlim(0, np.max(data[:2]))
    # plt.ylim(0, np.max(data[:1]))
    plt.xlim(0, 100000)
    plt.ylim(0, 100000)





    plt.subplot(223)
    plt.xlabel('K')
    plt.ylabel('M')
    plt.title("A-Matrix Shape: Total Time")
    times = np.multiply(data[:,3], data[:, 4])
    xs, ys, vals = [], [], []
    for key in aggregated_mk:
        ys.append(key[0])
        xs.append(key[1])
        vals.append(aggregated_mk[key][1])
    print(max(vals), sum(vals))
    plt.scatter(xs, ys, s=[(x/1500.0)*area_mod for x in vals], c='c', alpha=0.5)
    plt.xscale("log")
    plt.yscale("log")
    # plt.xlim(0, np.max(data[:0]))
    # plt.ylim(0, np.max(data[:2]))
    plt.xlim(0, 100000)
    plt.ylim(0, 100000)

    plt.subplot(224)
    plt.xlabel('N')
    plt.ylabel('K')
    plt.title("B-Matrix Shape: Total Time")
    xs, ys, vals = [], [], []
    for key in aggregated_kn:
        ys.append(key[0])
        xs.append(key[1])
        vals.append(aggregated_kn[key][1])
    print(max(vals), sum(vals))
    plt.scatter(xs, ys, s=[(x/1500.0)*area_mod for x in vals], c='c', alpha=0.5)
    plt.xscale("log")
    plt.yscale("log")
    # plt.xlim(0, np.max(data[:2]))
    # plt.ylim(0, np.max(data[:1]))
    plt.xlim(0, 100000)
    plt.ylim(0, 100000)

    plt.savefig(args.outFile+".pdf")



# Footer for catching no main
if __name__ == '__main__':
    main()