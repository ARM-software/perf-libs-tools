/*
    perf-libs-tools
    Copyright 2017 Arm Limited. 
    All rights reserved.
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int main()
{
  int nrows, i, LDA, LDB, LDC, M, N, K, ra, ca, rb, cb;
  long long int nn=0, nt=0, tn=0, tt=0, nCalls;
  int *data;
  float *fdata;
  char TRANSA, TRANSB, fstring[32];
  float cputime, tt_t=0.0, nn_t=0.0, nt_t=0.0, tn_t=0.0;  
  FILE *fptr;
  int NDATA=7;
  /*
  	data[0] = M;
  	data[1] = N;
  	data[2] = K;
  	data[3] = TRANSA;
  	data[4] = TRANSB;
  	data[5] = LDA>M;
  	data[6] = LDB>N;
  */

  //fptr = fopen("/tmp/.inp-jaswoo01", "r");
  printf("In main.\n");
  char *uname = getenv("USER");
  if (uname == NULL) {
	printf("Error failed to find $USER\n");
    exit(1);
  }

  static const char fileRoot[] = "/tmp/.inp-";
  char *fname = NULL;
  fname = (char *)calloc(sizeof(fileRoot)+sizeof(uname)+1,sizeof(char));
  if (fname == NULL) {
    printf("Error allocating fname of %d bytes\n",sizeof(fileRoot)+sizeof(uname)+1);
	exit(1);
  }
  fname[0] = '\0';
  strcat(fname,fileRoot);
  strcat(fname,uname);
  
  printf("File opening...\n");
  fptr = fopen(fname, "r");
  if (fptr == NULL) {
	printf("Error opening file %s\n",fname);
	exit(1);
  }
  free(fname); fname = NULL;
  printf("File open\n");

  fscanf(fptr,"%d %d %d\n", &nrows);
  if (nrows<1)
  {
  	printf("No dgemm data found\n");
  	return 0;
  }
  printf("Reading %d rows...\n", nrows);
  
  data = calloc(25*NDATA, sizeof(int));
  fdata = calloc(25*NDATA, sizeof(int));
  
  for (i=0; i<nrows; i++)
  {
  	fscanf(fptr,"%s %d %f %d %d %d %d %d %d %c %c", fstring, &nCalls, &cputime, &M, &N, &K, &LDA, &LDB, &LDC, &TRANSA, &TRANSB);
	if (M==0 || N==0 || K==0) continue;
  	ra = (int)(log10((float)(M)));
  	cb = (int)(log10((float)(N)));
  	ca = rb = (int)(log10((float)(K)));
  	/*printf("M=%5d K=%5d N=%5d     ra=%d ca=%d  rb=%d cb=%d   <%d>  <%d>\n", M, K, N, ra, ca, rb, cb, (ra+5*ca)*NDATA+0, (rb+5*cb)*NDATA+1);*/
  	data[(5*ra+ca)*NDATA+0]+=nCalls;
  	data[(5*rb+cb)*NDATA+1]+=nCalls;
  	
  	fdata[(5*ra+ca)*NDATA+0]+=cputime*nCalls;
  	fdata[(5*rb+cb)*NDATA+1]+=cputime*nCalls;
  	/*printf("TA=%c TB=%c\n", TRANSA, TRANSB);*/
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
  	if (LDA>M) data[(ra+5*ca)*NDATA+5]+=nCalls;
  	if (LDB>K) data[(rb+5*cb)*NDATA+6]+=nCalls;
  	
  }
  /*printf("Data read\n");*/

  fclose(fptr);
  fptr = fopen("/tmp/armpl.dgemm", "w");
  /* Print A-shape */
  for (i=0; i<5; i++)
  {
  	fprintf(fptr, "%d %d %d %d %d\n", data[5*i*NDATA], data[5*i*NDATA+NDATA], data[5*i*NDATA+2*NDATA], data[5*i*NDATA+3*NDATA], data[5*i*NDATA+4*NDATA]);
  }
  /* Print B-shape */
  for (i=0; i<5; i++)
  {
  	fprintf(fptr, "%d %d %d %d %d\n", data[5*i*NDATA+1], data[5*i*NDATA+NDATA+1], data[5*i*NDATA+2*NDATA+1], data[5*i*NDATA+3*NDATA+1], data[5*i*NDATA+4*NDATA+1]);
  
  }
  /* Print TRANS data */
  fprintf(fptr, "%ld %ld %ld %d -1\n", nn, nt, tn, tt);
  fprintf(fptr, "%12.8f %12.8f %12.8f %12.8f -1.0\n", nn_t, nt_t, tn_t, tt_t);

  /* Print A CPU times */
  for (i=0; i<5; i++)
  {
  	fprintf(fptr, "%f %f %f %f %f\n", fdata[5*i*NDATA+0], fdata[5*i*NDATA+NDATA+0], fdata[5*i*NDATA+2*NDATA+0], fdata[5*i*NDATA+3*NDATA+0], fdata[5*i*NDATA+4*NDATA+0]);
  
  }
  /* Print B CPU times */
  for (i=0; i<5; i++)
  {
  	fprintf(fptr, "%f %f %f %f %f\n", fdata[5*i*NDATA+1], fdata[5*i*NDATA+NDATA+1], fdata[5*i*NDATA+2*NDATA+1], fdata[5*i*NDATA+3*NDATA+1], fdata[5*i*NDATA+4*NDATA+1]);
  }
  
  fclose(fptr);
  
  return 0;
}
