# Updates - Jan 2019

1. Updated `summary.c` to be thread safe, and work with and OpenMP. (credit Chris Goodyer, ARM)
2. Added `PROTOTYPES_INC_MATH` for tracing `math.h` functions. (credit. Chris Goodyer, ARM)
3. `blas_usage.py` now takes a filename, for saving the graph as a pdf. 
4. Fixed `heat_dgemm.py` from standardising to nonsense value. Original included for reference.
5. Fixed `process-dgemm.c` overflow error.
6. Made sure that `process-dgemm.sh` now clears previous temp files that were accumulating. 
7. Included new graph generation file, `scatter_dgemm.sh` for better heat map visualisation. 

