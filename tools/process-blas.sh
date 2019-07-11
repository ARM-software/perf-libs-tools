#!/bin/bash

if [ "$1" == "" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ] ;
then
	echo "Usage ./process-blas.sh <files>" 
	exit
elif [ ! -f $1 ] ;
then
	echo "File $1 does not exist"
	exit
fi

#gcc -o Process-blas process-blas.c -O2 -lm

BLAS1="rotg_ rotmg_ rot_ rotm_ swap_ scal_ copy_ axpy_ dot_ dotu_ dotc_ nrm2_ asum_ amax_"
BLAS2="gemv_ gbmv_ hemv_ hbmv_ hpmv_ symv_ sbmv_ spmv_ trmv_ tbmv_ tpmv_ trsv_ tbsv_ tpsv_ ger_ geru_ gerc_ her_ hpr_ her2_ hpr2_ syr_ spr_ syr2_ spr2_"
BLAS3="gemm_ symm_ hemm_ syrk_ herk_ syr2k_ her2k_ trmm_ trsm_"

: "${TMPDIR:=/tmp}"
TMPFILE=${TMPDIR}/.inp-$USER
OUTFILE=${TMPDIR}/armpl.blas

cat $* > $TMPFILE
rm -f $OUTFILE

for stemroutine in $BLAS1 $BLAS2 $BLAS3
do	
#	echo $stemroutine >> $OUTFILE
	for routine in s$stemroutine d$stemroutine c$stemroutine z$stemroutine
	do
		grep $routine $TMPFILE | awk '{print $4}' | awk -v bsum=0.0 '{ bsum += $1 } END { print bsum }' >> $OUTFILE
		grep $routine $TMPFILE | awk '{print $4 " " $6}' | awk -v sum=0.0 '{ sum += $1 * $2 } END { print sum }' >> $OUTFILE
	done
done

#./Process-blas

rm -f $TMPFILE
