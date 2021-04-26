================================================================================
perf-libs-tools         Copyright 2017-21 Arm Limited        All rights reserved
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
   your build of Arm Performance Libraries.  This version matches 21.0.  Note 
   you can build using either GCC or Arm Compiler, however an Arm Performance 
   Libraries or Arm Compiler module must have been loaded to add the correct 
   directory containing 'armpl.h' to your path.

2) From this top level directory type "make".

You should now have a "lib/libarmpl-summarylog.so" created.


Usage
-----

1) Use LD_PRELOAD to pick-up the newly created logging library:

     export LD_PRELOAD=$PWD/lib/libarmpl-summarylog.so

   If your application is itself threaded you should use the library
   libarmpl_mp-summarylog.so instead as this will enable correct logging from 
   the different threads all calling Arm Performance Libraries functions 
   concurrently.

2) When you are building your application ensure that you are linking in 
   the shared library (e.g. libarmpl_lp64_mp.so) 
   rather than the static library (e.g. libarmpl_lp64_mp.a).

3) Run your application as normal.  Output files will be produced in the /tmp/
   directory when the program completes.  These will be called 
   /tmp/armplsummary_<pid>.apl where <pid> is the process ID.
   Note an extra line is added to the output of your program reading 
   
  Arm Performance Libraries output summary stored by default in files named
  
     /tmp/armplsummary_16776.apl 
   
  with the appropriate PID included.  The root of this can be modified using
  the environment variable ARMPL_SUMMARY_FILEROOT.

4) For certain applications we have seen situations where programs do not 
   terminate as expected, for instance if they are killed, crash, or are forked
   from Python.  In these cases it can be useful to have intermediate output 
   files written during the execution.  In order to use this functionality use 
   the environment variable ARMPL_SUMMARY_FREQ to set an initial frequency of
   library calls between each output.  By default this frequency grows by 10% 
   each output in order to limit the overhead in cases where the user has 
   little knowledge of the number of cases expected.  

   If using this frequency output, these extra output files will have an
   additional subscript in the name written, e.g.

     /tmp/armplsummary_16776_01.apl

   This is because a terminating program may die mid-write of the output file,
   hence allowing multiple file names to be iterated around means you can check
   which was the latest output.  

Note we have also included the library "lib/libarmpl-logger.so" which is used in 
the same way, however this gives much more verbose output producing an output 
line for every single library call.  The file root for output here is set
using ARMPL_LOGGING_FILEROOT.

   
Output
------

The output files generated list the following information:

	Column 1 : "Routine:"
	Column 2 : <routine name>
	Column 3 : "nCalls:"
	Column 4 : <number of calls>
	Column 5 : "Mean_time"
	Column 6 : <mean time of this call>
	Column 7 : "nUserCalls:"
	Column 8 : <number of top level calls>
	Column 9 : "Mean_user_time:"
	Column 10 : <mean time of this top-level call>
	Column 11 : "Inputs:"
	Column 12 onwards : input parameters to routine, integers then characters

That is, at the end of the execution of a program a summary list is produced 
itemizing each of the routines called, detailing the input cases that it has 
been called with, and then calculating the mean time taken for those inputs.

Only the integer and character parameters are recorded in this output.  This is
because the input cases of matrix contents should not normally be relevant to
understanding the cases used.  It does mean certain input parameters, such as
ALPHA and BETA for a DGEMM case, are missed, however this is an acceptable 
situation for the automatic creation of a logging library.

Note that we now provide two sets of timing results: inclusive and top-level.
Typically users may call a routine such as DPOTRF, but internally they may 
in turn call many other LAPACK or BLAS functions.  

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

---Overall library usage---

./process_summary.py <input files>
     This produces information about all library calls made.  A high-level 
     summary is returned, folllowed by break-downs of all the calls to each 
     library component (BLAS, LAPACK, FFT).  This data is split into output
     summarising both the total of calls and time spent in the function, and 
     also the number and time spent in this function from just user-called 
     invocations.
     
     For FFT calls this data also matches planning and execution stages 
     enabling detailed profliing of fftw_execute() calls with only a pointer.
     
     An additional file generated is the BLAS summary data, previously 
     produced by "./process-blas.sh", which can be fed into "./blas_usage.py", 
     see below.
     
    Input: One or more /tmp/armplsummary_<pid>.apl files.
    Output: <text> and /tmp/armpl.blas


---DGEMM calls---

./process-dgemm.sh <input files>
    This produces summary information about GEMM calls made in an application.

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

    Input: /tmp/armpl.dgemm
    Output: A matplotlib window showing usage.

---BLAS calls---

./process-blas.sh
    DEPRECATED -- use "./process-summary.py" instead

    This produces summary information about BLAS calls made in an application.
    
    Input: One or more /tmp/armplsummary_<pid>.apl files.
    Output: /tmp/armpl.blas

./blas_usage.py
    This visualizes the data from an armpl.blas file generated by 
    'process_summary.py'.
    
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

    Input: /tmp/armpl.blas.
    Output: A matplotlib window showing usage.


Known issues
------------

* If being used with GCC it is necessary to remove the functions cdotc_, cdotu_, 
  zdotc_ and zdotu_ from src/PROTOTYPES.  For convenience these are the first 
  four lines of that file.

* The top level call timings do not work when called from within a nested OpenMP 
  parallel regions.  Set your code to use only one level of OpenMP.

* For certain codes that create enormous numbers of FFTW plans then it may 
  be necessary to prevent trying to match plans with executes.  This situation 
  would result in a significant, and worsening, run-time performance of the 
  application.  This is not detailed here, but instructions can be made 
  available upon request.
