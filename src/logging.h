/*
    perf-libs-tools
    Copyright 2017 Arm Limited. 
    All rights reserved.
*/

#ifndef ARMPL_LOGGING
#define ARMPL_LOGGING

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdarg.h>
#include <unistd.h>
#include <sys/types.h>

/* Datatype for recording detail on what is recorded */

typedef struct armpl_logging_td
{
  char NAME[32];
  int numIargs;
  int numCargs;
  struct timespec ts_start;
  struct timespec ts_end;
  int *Iinp;
  char *Cinp;

} armpl_logging_struct;

/* Prototypes for logging functions */

#ifdef __cplusplus
extern "C" {
#endif
void armpl_logging_enter(armpl_logging_struct *logger, const char *FNC, int numVinps, int numIinps, int numCinps, ...);
void armpl_logging_leave(armpl_logging_struct *logger);
void armpl_set_value_int(const int *input);
int armpl_get_value_int(void);
FILE *armpl_open_logging_file(const char *fname);
FILE* armpl_ret_logging_file(void);
void armpl_close_logging_file(void);
#ifdef __cplusplus
}
#endif


#endif
