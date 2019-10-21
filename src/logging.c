/*
    perf-libs-tools
    Copyright 2017 Arm Limited. 
    All rights reserved.
*/

#include "logging.h"

int unsafe_val=0;
FILE *unsafe_fptr;

/* Routine called at start of ARMPL function to record details of function call into the logger structure */

void armpl_logging_enter(armpl_logging_struct *logger, const char *FNC, int numVinps, int numIinps, int numCinps, ...)
{
  int i, j, dimension=0, loc=0;
  va_list ap;

  sprintf(logger->NAME, "%s", FNC);

  va_start(ap, numCinps);
  
  if (numVinps>0)
  	dimension = va_arg(ap, int);

  logger->numIargs = numIinps;
  if (numVinps>0) logger->numIargs += numVinps*dimension+1;
  logger->numCargs = numCinps;

  if (numIinps+numVinps>0)
  {
  	logger->Iinp = malloc(sizeof(int)*logger->numIargs);
  	
  	loc=0;

        if (numVinps>0)
        {
		logger->Iinp[loc] = dimension;
		loc++;
	
	  	for (i = 0; i<numVinps; i++)
	  	{
	  		int *dataPtr = va_arg(ap, int*);
	  		for (j = 0; j<dimension; j++)
  			{
		  		logger->Iinp[loc] = dataPtr[j];
		  		loc++;
		  	}
  		}
  	}
  	for (i = 0; i<numIinps; i++)
  	{
  		logger->Iinp[loc] = va_arg(ap, int);
  		loc++;
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
  char *USERENV=NULL, name_root[64];
  clock_gettime(CLOCK_MONOTONIC, &logger->ts_end);

  if (firsttime==1)
  {
  	char fname[32];
  	/* Generate a "unique" filename for the output */
  	USERENV = getenv("ARMPL_LOGING_FILEROOT");
  	if (USERENV!=NULL && strlen(USERENV)>1) 
  		sprintf(name_root, "%s", USERENV);
  	else
  		sprintf(name_root, "/tmp/armpllog_");
  	sprintf(fname, "%s%.5d.apl", name_root, armpl_get_value_int());

  	fptr = armpl_open_logging_file(fname);
  	firsttime=0;
  }

  fprintf(fptr, "%s   ", logger->NAME);

  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec < 0 ) { logger->ts_end.tv_nsec+=1000000000; logger->ts_end.tv_sec-=1;}
  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec > 1000000000 ) { logger->ts_end.tv_nsec-=1000000000; logger->ts_end.tv_sec+=1;}
/*
  fprintf(fptr, "\t %d.%.9d\t",
  	logger->ts_end.tv_sec - logger->ts_start.tv_sec, logger->ts_end.tv_nsec - logger->ts_start.tv_nsec);
*/
  if (logger->numIargs > 0)
  {
  	for (i = 0; i<logger->numIargs; i++)
  		fprintf(fptr, "%ld ", (long) logger->Iinp[i]);
  }
  if (logger->numCargs > 0)
  {
  	for (i = 0; i<logger->numCargs; i++)
  		fprintf(fptr, "%c ", logger->Cinp[i]);
  }
  if (logger->numIargs > 1) free(logger->Iinp);
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



