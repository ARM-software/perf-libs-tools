/*
    perf-libs-tools
    Copyright 2017 Arm Limited. 
    All rights reserved.
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <unistd.h>

void printUsage(const char **funcNames, int maxFuncNames) {
	printf("Usage: process-dgemm [function name ID] filename [filename] [filename] etc.\n");
	printf("Default function: name = %s [ID=0]\n",funcNames[0]);
	printf("Function IDs: ");
	for (int i = 0; i < maxFuncNames; i++) {
		if (i == 0) { printf("%d=%s",i,funcNames[i]); }
		else { printf(",%d=%s",i,funcNames[i]); }
	}
	printf("\n");
}

int main(int argc, char** argv)
{
  int nrows, ncols, maxdim, i, j, LDA, LDB, LDC, M, N, K, ra, ca, rb, cb;
  long long int nn=0, nt=0, tn=0, tt=0, nCalls, dummy_l=0;
  int *data;
  float *fdata;
  char TRANSA, TRANSB, fstring[32];
  float cputime, tt_t=0.0, nn_t=0.0, nt_t=0.0, tn_t=0.0, dummy_f=0.0;  
  FILE *fptr;
  int NDATA=7;
	const char *funcNames[]={"dgemm","sgemm","zgemm","cgemm"};
	int maxFuncNames = 4;
	int funcNameID = 0;
	int fnameArg = 1;

/* The generated file is read by numpy which expects the same number of elements in each line, and the */
/* shortest line is 5 (which can be padded with zero if line length is greater). */
#define MIN_COLS 5
/* The search string used to grep through the file. Contains the %s to allow the filename to be inserted at runtime */
#define SEARCH_STR "grep %s %s |awk '{print $2 \" \" $4 \" \" $6 \" \" $12 \" \" $13 \" \" $14 \" \" $15 \" \" $16 \" \" $17 \" \" $18 \" \" $19 \" \" $20}'"

	/* Check args */
	if (argc < 2 || ( argc == 2 && (0==strcmp(argv[1],"-h") || 0==strcmp(argv[1],"--help")) ) ) {
		printf("Error: missing file name\n");
		printUsage(funcNames,maxFuncNames);
		exit(1);
	}
	/* If more than 2 args, try and sort out whether they are all filenames or a number */
	if (argc > 2) {
		/* lets assume the first arg is a function ID, if its not a valid number then assume */
		/* its the first of many filenames and test to see if it exists */
		char *testPtr;
		funcNameID = (int)strtol(argv[1],&testPtr,10);
		if (*testPtr != '\0') {
			/* not a valid number */
			fnameArg = 1;
		}
		else {
			/* valid number */
			fnameArg = 2;
		}
		if ((funcNameID < 0) || (funcNameID >= maxFuncNames)) {
			printf("Error: function name ID %d out of range of [0:%d]\n",funcNameID,maxFuncNames);
			printUsage(funcNames,maxFuncNames);
			exit(1);
		}
	}

	/* Check file exists */
	int fileNameLen = strlen(argv[fnameArg]);
	for (i = fnameArg; i < argc; i++) {
		if( access( argv[i], F_OK ) == -1 ) {
			printf("Error: can't access file %s\n",argv[i]);
			printUsage(funcNames,maxFuncNames);
   		 	exit(1);
		}
		if (strlen(argv[i]) > fileNameLen)
			fileNameLen = strlen(argv[i]);
	}

	FILE *fp;
	char path[1035]; // arbitrary size . . .

	/* Open the command for reading. */
	int funcNameLen = strlen(funcNames[funcNameID]);
	int searchComStrLenTotal = strlen(SEARCH_STR)+funcNameLen+fileNameLen+1; 
	char *searchComStr = calloc(searchComStrLenTotal,sizeof(char));
	if (searchComStr == NULL) {
		printf("Error: failed to allocate strinf %d bytes\n",searchComStrLenTotal);
		exit(1);
	}

	nrows = 0;
	maxdim = 0;
	for (i = fnameArg; i < argc; i++) {
		snprintf(searchComStr,searchComStrLenTotal-1,SEARCH_STR,funcNames[funcNameID],argv[i]);
		
		/* Run search command 1st time and get access to return results to get metrics */
		fp = popen(searchComStr,"r");
		if (fp == NULL) {
			printf("Failed to run command\n" );
			exit(1);
		}
		
		/* Read the output a line at a time - output it. */
		while (fgets(path, sizeof(path), fp) != NULL) {
			//printf("%s", path);
			sscanf(path,"%s %lld %f %d %d %d %d %d %d %c %c", fstring, &nCalls, &cputime, &M, &N, &K, &LDA, &LDB, &LDC, &TRANSA, &TRANSB);
			if (M > maxdim) maxdim = M;
			if (N > maxdim) maxdim = N;
			if (K > maxdim) maxdim = K;
			nrows++;
		}
		
		/* close */
		pclose(fp);
	}

	/* Exit of no rows found */
	if (nrows == 0) {
		printf("No %s function calls found in input files\n",funcNames[funcNameID]);
		exit(0);
	}

	/* convert size of maxdim into the number of suares to create */
	ncols = 0;
	while (maxdim) {
		maxdim /= 10;
		ncols++;
	}

	/* Not sure this could happen, but having 0 certainly would be a problem */
	if (ncols < MIN_COLS)
		ncols = MIN_COLS;

	//printf("Nrows = %d\n",nrows);
	//printf("Ncols = %d\n",ncols);

	data = calloc((ncols*ncols)*NDATA, sizeof(int));
	fdata = calloc((ncols*ncols)*NDATA, sizeof(int));
  
	/* Run search command 2nd time and get access to return results to get data */
	for (i = fnameArg; i < argc; i++) {
		snprintf(searchComStr,searchComStrLenTotal-1,SEARCH_STR,funcNames[funcNameID],argv[i]);
		fp = popen(searchComStr,"r");
		if (fp == NULL) {
			printf("Failed to run command\n" );
			exit(1);
		}
		
		/* Read the output a line at a time - output it. */
		while (fgets(path, sizeof(path)-1, fp) != NULL) {
			sscanf(path,"%s %lld %f %d %d %d %d %d %d %c %c", fstring, &nCalls, &cputime, &M, &N, &K, &LDA, &LDB, &LDC, &TRANSA, &TRANSB);
			//printf("fstring %s nCalls %d cputime %f M %d N %d K %d LDA %d LDB %d LDC %d TRANSA %c TRANSB %c\n", fstring, nCalls, cputime, M, N, K, LDA, LDB, LDC, TRANSA, TRANSB);
			if (M==0 || N==0 || K==0) continue;
			ra = (int)(log10((float)(M)));
			cb = (int)(log10((float)(N)));
			ca = rb = (int)(log10((float)(K)));
			data[(ncols*ra+ca)*NDATA+0]+=nCalls;
			data[(ncols*rb+cb)*NDATA+1]+=nCalls;
			
			fdata[(ncols*ra+ca)*NDATA+0]+=cputime*nCalls;
			fdata[(ncols*rb+cb)*NDATA+1]+=cputime*nCalls;
			if (TRANSA=='t' || TRANSA=='T') 
			{	
				if (TRANSB=='t' || TRANSB=='T') 
				{
					tt+=nCalls;
					tt_t+=cputime*nCalls;
				} else {
					tn+=nCalls;
					tn_t+=cputime*nCalls;
				}
			} else {
				if (TRANSB=='t' || TRANSB=='T') 
				{
					nt+=nCalls;
					nt_t+=cputime*nCalls;
				} else {
					nn+=nCalls;
					nn_t+=cputime*nCalls;
				}
			}
		
			if (LDA>M) data[(ra+ncols*ca)*NDATA+ncols]+=nCalls;
			if (LDB>K) data[(rb+ncols*cb)*NDATA+ncols]+=nCalls;
		}
		/* close */
		pclose(fp);
	}

	/* Open file for output */
	char *outFname = calloc(strlen("/tmp/armpl.")+strlen(funcNames[funcNameID])+1,sizeof(char));
	strcat(outFname,"/tmp/armpl.");
	strcat(outFname,funcNames[funcNameID]);
	fptr = fopen(outFname, "w");
	if (fptr == NULL) {
		printf("Error: failed to open output file %s\n",outFname);
		exit(1);
	}
	/* Print A-shape */
	for (i=0; i<ncols; i++) {
		for (j=0; j<ncols; j++) {
			fprintf(fptr, "%d ", data[ncols*i*NDATA+(j*NDATA)]);
		}
		fprintf(fptr,"\n");
	}
	/* Print B-shape */
	for (i=0; i<ncols; i++) {
		for (j=0; j<ncols; j++) {
			fprintf(fptr, "%d ", data[ncols*i*NDATA+j*NDATA+1]);
		}
		fprintf(fptr,"\n");
	
	}
	/* Print TRANS data */
	fprintf(fptr, "%lld %lld %lld %lld -1 ", nn, nt, tn, tt);
	for (i=MIN_COLS; i<ncols; i++) {
	    fprintf(fptr, "%lld ", dummy_l);
	}
	fprintf(fptr,"\n");
	fprintf(fptr, "%12.8f %12.8f %12.8f %12.8f -1.0 ", nn_t, nt_t, tn_t, tt_t);
	for (i=MIN_COLS; i<ncols; i++) {
	    fprintf(fptr, "%lf ", dummy_f);
	}
	fprintf(fptr,"\n");
	
	/* Print A CPU times */
	for (i=0; i<ncols; i++) {
		for (j=0; j<ncols; j++) {
			fprintf(fptr, "%f ", fdata[ncols*i*NDATA+j*NDATA+0]);
		}
		fprintf(fptr,"\n");
	
	}
	/* Print B CPU times */
	for (i=0; i<ncols; i++) {
		for (j=0; j<ncols; j++) {
			fprintf(fptr, "%f ", fdata[ncols*i*NDATA+j*NDATA+1]);
		}
		fprintf(fptr,"\n");
	}
	
	fclose(fptr);

	printf("Created file %s\n",outFname);
  
  return 0;
}
