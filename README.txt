================================================================================
perf-libs-tools          Copyright 2017 Arm Limited          All rights reserved
================================================================================

Tools to support Arm Performance Libraries
------------------------------------------

This project provides tools to enable users of HPC applications to understand 
which routines from Arm Performance Libraries are being called.

The main component of this suite is the logging library that produces output to 
summarize the key information about routines called.  A selection of Python 
scripts for visualizating some of this data is also included.


Licensing
---------

This project is distributed under an Apache 2.0 license, available in the file
LICENSE.  All inbound contributions will also be under this same licence.


Compiling
---------

1) Ensure that you are using the latest version of the logging library to match 
   your build of Arm Performance Libraries.  This version matches 18.0.

2) From this top level directory type "make".

You should now have a "lib/libarmpl-summarylog.so" created.


Usage
-----

1) Use LD_PRELOAD to pick-up the newly created logging library:

       export LD_PRELOAD=$PWD/lib/libarmpl-summarylog.so

2) When you building your application ensure that you are linking in 
   the shared library (e.g. libarmpl_lp64_mp.so) 
   rather than the static library (e.g. libarmpl_lp64_mp.a).

3) Run your application as normal.  Output files will be produced in the /tmp/
   directory when the program completes.  These will be called 
   /tmp/armplsummary_<pid>.apl where <pid> is the process ID.
   Note an extra line is added to the output of your program reading 
   
  Arm Performance Libraries output summary stored in /tmp/armplsummary_16776.apl 
   
   with the appropriate PID included.

Note we have also included the library "lib/libarmpl-logger.so" which is used in 
the same way, however this gives much more verbose output producing an output 
line for every single library call.

   
Output
------

The output files generated list the following information:

	Column 1 : "Routine:"
	Column 2 : <routine name>
	Column 3 : "nCalls:"
	Column 4 : <number of calls>
	Column 5 : "Mean_time"
	Column 6 : <mean time of this call>
	Column 7 : "Inputs:"
	Column 8 onwards : input parameters to routine, integers then characters

That is, at the end of the execution of a program a summary list is produced 
itemizing each of the routines called, detailing the input cases that it has 
been called with, and then calculating the mean time taken for those inputs.

Only the integer and character parameters are recorded in this output.  This is
because the input cases of matrix contents should not normally be relevant to
understanding the cases used.  It does mean certain input parameters, such as
ALPHA and BETA for a DGEMM case, are missed, however this is an acceptable 
situation for the automatic creation of a logging library.


Tools
-----

In the "tools/" directory are some example scripts to produce graphical summaries 
of the output produced from the logging library.  They are written using the 
Python package MatPlotLib, and we recommend running the visualization part of 
that script on a local machine rather than on a remote box.

At present we are seeing these as a two-stage process:
(1) process the /tmp/armplsummary_<pid>.apl output 
(2) visualize this output

There will be many more useful visualizations that can be done with this data, 
and we look forward to receiving additional contributions.

All tools, at present, are written to be run from the "tools" directory so you 
need to

	cd tools

before following the instructions below.

---DGEMM calls---

./process-dgemm.sh <input files>
    This produces summary information about DGEMM calls made in an application.

    Input: One or more /tmp/armplsummary_<pid>.apl files.
    Output: /tmp/armpl.dgemm
    
./heat_dgemm.py
    This visualizes the data from an armpl.dgemm file.

    Usage: heat_dgemm.py [-h] [-i INFILE] [-l]
    Optional arguments:
       -h, --help                 Show help message and exit
       -i INFILE, --input INFILE  Input file
       -l, --legend               Show graph legend
        
    What does it show?
       Two rows, each with two heat maps and a pie chart
       The top row shows the number of calls made.
       The bottom row shows the time spent.
       The heat maps show the proportion of calls/time at each problem dimension 
       for matix A (left) and B (right).
       The pie charts show the proportion of calls/time for the given transpose 
       options for matrices A and B.

---BLAS calls---

./process-blas.sh
    This produces summary information about BLAS calls made in an application.
    
    Input: One or more /tmp/armplsummary_<pid>.apl files.
    Output: /tmp/armpl.blas

./blas_usage.py
    This visualizes the data from an armpl.blas file.
    
    Usage: blas_usage.py [-h] [-l] [-n] [-x] [-i INFILE]
    Optional arguments:
      -h, --help                  Show help message and exit
      -i INFILE, --input INFILE   Input file
      -l, --legend                Show graph legend
      -n, --normalize             Normalize bars to percentages of max
      -x, --exclude               Exclude unrepresented functions

    What does it show?
        Two sets of three rows of bar charts:
          Top set: Number of calls
          Bottom set: Time spent in these calls
          
        For each set:
          Top row: BLAS level 1 routines
          Middle row: BLAS level 2 routines
          Bottom row: BLAS level 3 routines
        
        On each row different families of functions are shown, for example GEMM.
        For each family different bars show the number of routines of:
            single precision real (red)
            double precision real (blue)
            single precision complex (yellow)
            double precision complex (green)
            
        Useful additional option include "-x" to exclude routines that are never 
        called and "-n" to normalise time taken against the most expensive 
        routine.

