/*
    perf-libs-tools
    Copyright 2017 Arm Limited. 
    All rights reserved.
*/

#include "logging.h"

int unsafe_val=0;
FILE *unsafe_fptr;

/* Routine called at start of ARMPL function to record details of function call into the logger structure */

void armpl_logging_enter(armpl_logging_struct *logger, const char *FNC, int numIinps, int numCinps, ...)
{
  int i;
  va_list ap;

  sprintf(logger->NAME, "%s", FNC);

  va_start(ap, numCinps);

  logger->numIargs = numIinps;
  logger->numCargs = numCinps;

  if (numIinps>0)
  {
  	logger->Iinp = malloc(sizeof(int)*numIinps);

  	for (i = 0; i<numIinps; i++)
  	{
  		logger->Iinp[i] = va_arg(ap, int);
  	}

  }

  if (numCinps>0)
  {
  	logger->Cinp = malloc(sizeof(char)*numCinps);

  	for (i = 0; i<numCinps; i++)
  	{
  		logger->Cinp[i] = (char) va_arg(ap, int);
  	}
  }

  va_end(ap);

  clock_gettime(CLOCK_MONOTONIC, &logger->ts_start);
  return;
}

/* Routine called at end of ARMPL function that records data to output file including timing */

void armpl_logging_leave(armpl_logging_struct *logger)
{
  int i;
  static int firsttime=1;
  static FILE *fptr;
  clock_gettime(CLOCK_MONOTONIC, &logger->ts_end);

  if (firsttime==1)
  {
  	char fname[32];
  	sprintf(fname, "/tmp/armpllog_%.5d.apl", armpl_get_value_int());

  	fptr = armpl_open_logging_file(fname);
  }

  fprintf(fptr, "%s   ", logger->NAME);

  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec < 0 ) { logger->ts_end.tv_nsec+=1000000000; logger->ts_end.tv_sec-=1;}
  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec > 1000000000 ) { logger->ts_end.tv_nsec-=1000000000; logger->ts_end.tv_sec+=1;}

  fprintf(fptr, "\t %d.%.9d\t",
  	logger->ts_end.tv_sec - logger->ts_start.tv_sec, logger->ts_end.tv_nsec - logger->ts_start.tv_nsec);

  if (logger->numIargs > 0)
  {
  	for (i = 0; i<logger->numIargs; i++)
  		fprintf(fptr, "%d ", logger->Iinp[i]);
  }
  if (logger->numCargs > 0)
  {
  	for (i = 0; i<logger->numCargs; i++)
  		fprintf(fptr, "%c ", logger->Cinp[i]);
  }

  if (logger->numIargs > 0) free(logger->Iinp);
  if (logger->numCargs > 0) free(logger->Cinp);

  fprintf(fptr, "\n");

}

/* Utility functions for accessing global data */

void armpl_set_value_int(const int *input) {
	unsafe_val=*input;
	return ;
}

int armpl_get_value_int(void) {
	return getpid();
}

FILE *armpl_open_logging_file(const char *fname) {
	static int firsttime = 1;
	if (firsttime==1)
	{
		unsafe_fptr = fopen(fname, "w");
		firsttime = 0;
	}
	return unsafe_fptr;
}

FILE* armpl_ret_logging_file(void) {
	return unsafe_fptr;
}

void armpl_close_logging_file(void) {
	fclose(unsafe_fptr);
	return;
}



