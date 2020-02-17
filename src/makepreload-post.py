#!/usr/bin/env python

#    perf-libs-tools
#    Copyright 2017 Arm Limited. 
#    All rights reserved.
#

# Program to turn armpl.h into a library that can be preloaded to do logging

# 1. Manually preprocess armpl.h into PROTOTYPES to only have the BLAS/LAPACK/FFT prototypes - no semicolons!
# 2. Create output file and add header line
# 3. Loop over lines of PROTOTYPES
#    a. Read line
#    b. Get interface details
#    c. Make logging function
#       i. Prototype line without semicolon and a following bracket
#      i2. Declare "armpl_logging_struct logger;"
#      ii. Count <num_integer> and <num_char> porameters that we'll record
#     iii. "armpl_logging_enter(&logger, <fn_name>, <num_integer>, <num_char>," followed by list of integers and chars with dereferences but not types, ");"
#      iv. "real_<fn_name> = dlsym(RTLD_NEXT, "<fn_name>");"
#       v. Call line to "real_<fn_name>" without types and dereferencing
#      vi. "armpl_logging_leave(&logger," followed by list of integers and chars with dereferences but not types, ");"
#     vii. return <return_val>
#    viii. Closing bracket

# NOTES :
#        At present LAPACKE functions are not in as:
#        * not recording the right data as derefencing stage is wrong in the armpl_logging_enter call
#        * the presence of const all over the place
#        * most importantly they just call the versions with underscores at the end

import re		# Regular expressions toolbox
import itertools	# Iteration toolbox

def main(args=None):

  # Load appropriately made file
  fname = "PROTOTYPES"
  inputfile = open(fname, 'r')

  # Create output file (Step 2)
  fname = "preload-sumgen.c"
  outputfile = open(fname, 'w')
  outputfile.write('#include "preloadlib.h"\n\n')

  # Loop over input lines (Step 3 - inc step3a)
  for line in  inputfile:

     IargsToLog = []
     VargsToLog = []
     CargsToLog = []
     DEREFEDARGS = ""
     PRELIMS = "\tint armpl_logging_var_dimension=0;\n"
     POSTLIMS = ""

     # First get interface details
     splitline = re.findall(r"[\w']+", line)
     ReturnType = splitline[0]
     FNNAME = splitline[1]
     REAL_FNNAME = "(*real_%s)" % FNNAME
     prototype = line.replace(FNNAME, REAL_FNNAME)

     # Now make logging function (Step 3.c.i)
     outputfile.write("%s{\n" % line)
     if (ReturnType != "void") :
        outputfile.write("\t%s returnVal;\n" % ReturnType)
     outputfile.write("\tarmpl_logging_struct logger;\n")
     # Count int and char parameters for recording (Step 3.c.ii)
     numI = line.count("armpl_int_t")+line.count("fftwplan")
     numV = line.count("armpl_int_v")
     numC = line.count("char")

     # deduct any return values
     if ( splitline[0] == "armpl_int_t") :
        numI = numI-1
     if ( splitline[0] == "fftwplan") :  # note we actually add this back in later!
        numI = numI-1
     if ( splitline[0] == "armpl_int_t_c") :
        numI = numI-1
     if ( splitline[0] == "char") :
        numC = numC-1

     # if we have at least one vector, one of the entries will be the dimension, which we shall send as first 'vector' entry
     if (numV > 0) :
        numI = numI-1

     for entry in range (2, len(splitline), 2) :
        if (splitline[entry] == "void") :
           break

        # Handle special case where this variable is a rank of dimensions
        # Note we assume that this dimension is always given before any arrays that need to use it to loop over
        if ( splitline[entry] == "armpl_int_t_c_d") :
           VargsToLog.append("%s" % splitline[entry+1])
           PRELIMS2 = "%s \tarmpl_logging_var_dimension=%s;\n" % (PRELIMS, splitline[entry+1])
           PRELIMS=PRELIMS2
        
	DEREFEDARGS = "%s %s" % ( DEREFEDARGS, str(splitline[entry+1]))
        if (entry < len(splitline)-2) :
           DEREFEDARGS = "%s," % DEREFEDARGS

        if (splitline[entry] == "armpl_int_t") :
           IargsToLog.append("*%s" % splitline[entry+1])

        if (splitline[entry] == "armpl_int_v") :
           VargsToLog.append("%s" % splitline[entry+1])

        if (splitline[entry] == "armpl_int_t_c") :
           IargsToLog.append("%s" % splitline[entry+1])

        if (splitline[entry] == "armpl_int_t_N") :
           PRELIMS2 = "%s \tint I%d;\n \tif (%s!=NULL){I%d=inembed[0];}else{I%d=-1;}\n" % (PRELIMS, entry, splitline[entry+1], entry, entry)
           PRELIMS=PRELIMS2
           IargsToLog.append("I%d" % entry)

        if (splitline[entry] == "fftwplan") :
           IargsToLog.append("(int) %s" % splitline[entry+1])

        if (splitline[entry] == "char") :
           CargsToLog.append("*%s" % splitline[entry+1])

     # Add fftwplan to list of integers that will be returned
     if ( splitline[0] == "fftwplan") :
        numI = numI+1
        IargsToLog.append("returnVal")
        POSTLIMS = "logger.Iinp[logger.numIargs-1] = (int) returnVal;\n"

     # Make lists of arguments to record
     if (numI > 0) :
        Iargs = ", ".join(map(str, IargsToLog ) )           # Remove single quotes
        IargsToLog = ", ".join( repr(e) for e in Iargs )    # Remove square brackets
     if (numC > 0) :
        Cargs = ", ".join(map(str, CargsToLog ) )
        CargsToLog = ", ".join(map(str, CargsToLog ) )
     if (numV > 0) :
        Vargs = ", ".join(map(str, VargsToLog ) )
        VargsToLog = ", ".join(map(str, VargsToLog ) )

     # Record any extra prelims made in loop above
     outputfile.write("%s" % str(PRELIMS))

     # Start logging (Step 3.c.iii)
     outputfile.write('\tarmpl_logging_enter(&logger, "%s", %d, %d, %d, armpl_logging_var_dimension);\n' % (FNNAME, numV, numI, numC ) ) 

     # Do the symbol linking (Step 3.c.iv)
     outputfile.write('\t%s = dlsym(RTLD_NEXT, "%s");\n' % (prototype.rstrip('\n'), FNNAME))

     # Now call the function (Step 3.c.v)
     if (ReturnType != "void") :
        outputfile.write('\treturnVal = real_%s(%s);\n' % (FNNAME, DEREFEDARGS) )
     else :
        outputfile.write('\treal_%s(%s);\n' % (FNNAME, DEREFEDARGS) )

     # If we are recording a pointer to an FFTW plan then record this here
     outputfile.write("%s" % str(POSTLIMS))

     # Now finish function (Step 3.c.vi-vii)
     outputfile.write("\tarmpl_logging_leave(&logger")

     if (numV > 0) :
        outputfile.write(', %s' % (str(Vargs) ) )
     if (numI > 0) :
        outputfile.write(', %s' % (str(Iargs) ) )
     if (numC > 0) :
        outputfile.write(', %s' % (str(Cargs) ) )
     outputfile.write(');\n')


     if (ReturnType != "void") :
        outputfile.write("\treturn returnVal;\n")
     outputfile.write("}\n")


if __name__ == '__main__':
    main()

