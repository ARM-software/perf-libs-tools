/*
    perf-libs-tools
    Copyright 2017-20 Arm Limited. 
    All rights reserved.
*/

#include "summary.h"

#ifdef _OPENMP
#include <omp.h>
#endif

armpl_lnkdlst_t *listHead = NULL;

/* Routine to record log on standard program exits */

void armpl_summary_exit()
{
  armpl_lnkdlst_t *listEntry = listHead;
  armpl_lnkdlst_t *thisEntry = listHead;
  armpl_lnkdlst_t *nextEntry = listHead;
  FILE *fptr;
  char fname[64];
  static int firsttime=0;
  struct timespec armpl_progstop;
  double printingtime;
  char *USERENV=NULL, name_root[64];

  /* Stop the program timer */
  clock_gettime(CLOCK_MONOTONIC, &armpl_progstop);
  while (armpl_progstop.tv_nsec - armpl_progstart.tv_nsec < 0 ) { armpl_progstop.tv_nsec+=1000000000; armpl_progstop.tv_sec-=1;}
  while (armpl_progstop.tv_nsec - armpl_progstart.tv_nsec > 1000000000 ) { armpl_progstop.tv_nsec-=1000000000; armpl_progstop.tv_sec+=1;}

  
  /* Generate a "unique" filename for the output */
  USERENV = getenv("ARMPL_SUMMARY_FILEROOT");
  if (USERENV!=NULL && strlen(USERENV)>1) 
  	sprintf(name_root, "%s", USERENV);
  else
  	sprintf(name_root, "/tmp/armplsummary_");
  sprintf(fname, "%s%.5d.apl", name_root, armpl_get_value_int());
  fptr = fopen(fname, "w");

  fprintf(fptr, "Routine: main  nCalls: 1  Total_time %12.6e nCalls: 1  Total_time %12.6e \n", 
  	armpl_progstop.tv_sec - armpl_progstart.tv_sec + 1.0e-9*(armpl_progstop.tv_nsec - armpl_progstart.tv_nsec), 
  	armpl_progstop.tv_sec - armpl_progstart.tv_sec + 1.0e-9*(armpl_progstop.tv_nsec - armpl_progstart.tv_nsec));

  while (NULL != listEntry)
  {
  	thisEntry = listEntry;
  	nextEntry = listEntry->nextRoutine;
  	do
  	{
  		if (listEntry->callCount_top>0)
  		{
  			printingtime = listEntry->timeTotal_top/listEntry->callCount_top;
  		} else {
  			printingtime = 0.0;
  		}
  		fprintf(fptr, "Routine: %8s  nCalls: %6d  Mean_time %12.6e   nUserCalls: %6d  Mean_user_time: %12.6e   Inputs: %s\n", 
  				thisEntry->routineName, listEntry->callCount, listEntry->timeTotal/listEntry->callCount, 
  				listEntry->callCount_top, printingtime,
  				listEntry->inputsString);
		listEntry = listEntry->nextCase;
	} while (NULL != listEntry);
	
	listEntry = nextEntry;
  }

  fclose(fptr);
  printf("Arm Performance Libraries output summary stored in %s\n", fname);
  return;
}

/* Routine called at start of ARMPL function to record details of function call into the logger structure */

void armpl_logging_enter(armpl_logging_struct *logger, const char *FNC, int numVinps, int numIinps, int numCinps, int dimension)
{
  int totToStore;
  static int firsttime=1, firstthread=1;
  int *tmpI;

  if (1==firsttime) 
  {
  	firsttime = 0;
  	armpl_enable_summary_list();
  }

  sprintf(logger->NAME, "%s", FNC);

  logger->numIargs = numIinps;
  logger->numVargs = numVinps;
  logger->numCargs = numCinps;
  
  if (toplevel_global==0)
  {
  	toplevel_global = 1;
  	logger->topLevel = 1;
  } else {
  	logger->topLevel = 0;
  }

#ifndef _OPENMP
  if (toplevel_global==0)
  {
  	toplevel_global = 1;
  	logger->topLevel = 1;
  } else {
  	logger->topLevel = 0;
  }
#else
#pragma omp critical
{
  if (!omp_in_parallel() && logger->topLevel==2) /* i.e. were we previously in a parallel region but not any more, hence must be at the top level */
  {
	toplevel_global = 0;
	/* Note we don't need to clear toplevel_thread_global as all entries should already have been set to 0 */
  }

  if (toplevel_global==0)
  {
	/* Check if we are already in an OpenMP parallel section */
	if (!omp_in_parallel())
	{
		logger->topLevel = 1;
		toplevel_global = 1;
	} else {
		logger->topLevel = 2;
		toplevel_global = 2;
		{
			if (firstthread==1)
			{
				threadtot = omp_get_num_threads();
				printf("Allocating array length %d on thread %d...\n", threadtot, omp_get_thread_num());
				toplevel_thread_global = calloc(threadtot, sizeof(int));
				blas_top_openmp_level = omp_get_level();
				firstthread = 0;
			}
		}
		toplevel_thread_global[omp_get_thread_num()] = 1;
	}
  } else if (toplevel_global==1){
  	logger->topLevel = 0;
  } else /*i.e. toplevel_global==2 */ {
	if (omp_get_level()>blas_top_openmp_level)	/* in a nested parallelism region */
	{
		logger->topLevel = 0;
	} else if (toplevel_thread_global[omp_get_thread_num()]==0)	/* Top level for this thread */
	{
		toplevel_thread_global[omp_get_thread_num()]=1;
		logger->topLevel=2;
	} else {					/* Interior thread */
		logger->topLevel = 0;
	}
  }
}
#endif

#pragma omp critical
  {
  	totToStore = logger->numIargs;
  	if (logger->numVargs>0) totToStore += logger->numVargs*dimension+1;

  	if (totToStore>0)
  	{
  		logger->Iinp = calloc(totToStore, sizeof(int));
  	}
  }

  clock_gettime(CLOCK_MONOTONIC, &logger->ts_start);
  return;
}

/* Routine called at end of ARMPL function that records data to output file including timing */

void armpl_logging_leave(armpl_logging_struct *logger, ...)
{
  int i, j, dimension=0, loc=0, found;
  static FILE *fptr;
  armpl_lnkdlst_t *listEntry = listHead;
  int stringLen, totToStore;
  char *inputString;
  va_list ap;
  clock_gettime(CLOCK_MONOTONIC, &logger->ts_end);

  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec < 0 ) { logger->ts_end.tv_nsec+=1000000000; logger->ts_end.tv_sec-=1;}
  while (logger->ts_end.tv_nsec - logger->ts_start.tv_nsec > 1000000000 ) { logger->ts_end.tv_nsec-=1000000000; logger->ts_end.tv_sec+=1;}

  /* Store inputs */
  /* Note we are doing this after execution now so any output integers are also recorded to prevent false positives.
     This would mean if a routines had INOUT characters or integer arguments then it is the OUT not the IN that is recorded */

  va_start(ap, logger);
    
  if (logger->numVargs>0)
  	dimension = va_arg(ap, int);

  totToStore = logger->numIargs;
  if (logger->numVargs>0) totToStore += logger->numVargs*dimension+1;

  if (totToStore>0)
  {
  	loc=0;

        if (logger->numVargs>0)
        {
		logger->Iinp[loc] = dimension;
		loc++;
	
	  	for (i = 0; i<logger->numVargs; i++)
	  	{
	  		int *dataPtr = va_arg(ap, int*);
	  		for (j = 0; j<dimension; j++)
  			{
		  		logger->Iinp[loc] = dataPtr[j];
		  		loc++;
		  	}
  		}
  	}
  	for (i = 0; i<logger->numIargs; i++)
  	{
  		logger->Iinp[loc] = va_arg(ap, int);
  		loc++;
  	}

  }

  if (logger->numCargs>0)
  {
  	logger->Cinp = malloc(sizeof(char)*logger->numCargs);

  	for (i = 0; i<logger->numCargs; i++)
  	{
  		logger->Cinp[i] = (char) va_arg(ap, int);
  	}
  }
  va_end(ap);

  /* Summary information */

  /* Build delimited sting of inputs */
  	/* string length of 12 digits per integer, 1 character per char, add 1 extra each for delimiter, plus headroom at end */
  stringLen = totToStore*13+logger->numCargs*2+2;
  inputString = malloc(stringLen*sizeof(char));
  if (totToStore > 0)
  {
  	for (i = 0; i<totToStore; i++)
  	{
  		sprintf(&inputString[i*13], " %12d", logger->Iinp[i]);
  	}
  }
  if (logger->numCargs > 0)
  {
  	for (i = 0; i<logger->numCargs; i++)
  		sprintf(&inputString[logger->numIargs*13+2*i], " %c", logger->Cinp[i]);
  }
  sprintf(&inputString[totToStore*13+2*logger->numCargs], " ");
  
#pragma omp critical 
{
  /* Check if routine is in list already */
  found=0;

  listEntry = listHead;
  if (listEntry->callCount==-1)		/* New list */
  {
  		listEntry->routineName = malloc(sizeof(char)*strlen(logger->NAME)+1);
	  	sprintf(listEntry->routineName, "%s", logger->NAME);
	
	  	listEntry->inputsString = inputString;
	
	  	listEntry->callCount = 0;
	  	listEntry->timeTotal = 0.0;
	  	listEntry->callCount_top = 0;
	  	listEntry->timeTotal_top = 0.0;
  } else if (listEntry->nextRoutine==NULL && 0==strcmp(listEntry->routineName, logger->NAME))
  {					/* first entry */
  		found=1;
  } else {				/* Existing list */
  	while (1)
  	{
  		if (0==strcmp(listEntry->routineName, logger->NAME))
  		{
  			found=1;
  			break;
  		} 
  		if (NULL==listEntry->nextRoutine) break;
  		listEntry = listEntry->nextRoutine;
	}

	/* else:  new routine */
  	if (0 == found) 
	{
		listEntry->nextRoutine = malloc(sizeof(armpl_lnkdlst_t));
		listEntry = listEntry->nextRoutine;
	
  		listEntry->routineName = malloc(sizeof(char)*strlen(logger->NAME)+1);
	  	sprintf(listEntry->routineName, "%s", logger->NAME);
	  	
	  	listEntry->inputsString = inputString;
	
	  	listEntry->callCount = 0;
	  	listEntry->timeTotal = 0.0;
	  	listEntry->callCount_top = 0;
	  	listEntry->timeTotal_top = 0.0;
		listEntry->nextRoutine = NULL;
		listEntry->nextCase = NULL;
  	}
  }

  if (1 == found)
  {
  	/* Loop over current cases */
  	do
  	{
  		if (0 == strcmp(listEntry->inputsString, inputString))
  		{
  			found = 2;
  			break;
  		}
  		if (NULL != listEntry->nextCase)
  		{
  			listEntry = listEntry->nextCase;
  		} else {
  			listEntry->nextCase  = malloc(sizeof(armpl_lnkdlst_t));
  			listEntry = listEntry->nextCase;
  			
  			listEntry->inputsString = inputString;

  			listEntry->callCount = 0;
  			listEntry->timeTotal = 0.0;
  			listEntry->callCount_top = 0;
  			listEntry->timeTotal_top = 0.0;
  			listEntry->nextCase = NULL;
  			break;
  		}
  	} while (1);
  
  }


  /* Now update totals for this routine */
  listEntry->callCount++;
  listEntry->timeTotal += logger->ts_end.tv_sec - logger->ts_start.tv_sec + 1.0e-9*(logger->ts_end.tv_nsec - logger->ts_start.tv_nsec);

  /* Deal with top level calls */
  if (0 < logger->topLevel)
  {
  	listEntry->callCount_top++;
  	listEntry->timeTotal_top += logger->ts_end.tv_sec - logger->ts_start.tv_sec + 1.0e-9*(logger->ts_end.tv_nsec - logger->ts_start.tv_nsec);
#ifndef _OPENMP
  	toplevel_global = 0;
#else
	if (1==toplevel_global)
	{
		toplevel_global = 0;
	} else if (2==toplevel_global && omp_get_level()==blas_top_openmp_level)
	{
		toplevel_thread_global[omp_get_thread_num()]=0;
	}
#endif
  }


  if (logger->numIargs > 1) 
  {
  	free(logger->Iinp);
  	logger->Iinp = NULL;
  }
  if (logger->numCargs > 0) 
  {
  	free(logger->Cinp);
  	logger->Cinp = NULL;
  }

} /* End of OpenMP critical section */

}

/* Utility functions for accessing global data */

int armpl_get_value_int(void) {
	return getpid();
}

void armpl_enable_summary_list(void) {
	static int firsttime = 1;
	if (firsttime==1)
	{
		firsttime = 0;

		/* Register exit function */
		atexit(armpl_summary_exit);
		
		/* Create linked lists */
		listHead = malloc(sizeof(armpl_lnkdlst_t));
		
		listHead->callCount=-1;
    
		listHead->nextRoutine = NULL;
		listHead->nextCase = NULL;
		
		clock_gettime(CLOCK_MONOTONIC, &armpl_progstart);

	}

	return;
}

