#!/bin/bash

if [ "$1" == "" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ] ;
then
	echo "Usage ./process-dgemm.sh <files>"
	exit
fi

for f in $*
do
	if [ ! -f $f ] ;
	then
		echo "File $1 does not exist"
		exit
	fi
done

if [ ! -f Process-dgemm ] ;
then
	echo "Need to run './Process-dgemm'.  Either I am not in perf-libs-tools/tools or you need to compile:"
	echo "  $ gcc -o Process-dgemm process-dgemm.c"
fi

TMPFILE=/tmp/.inp-${USER}_[dszc]

rm -f $TMPFILE
for file in $*
do
	grep dgemm ${file} >> ${TMPFILE}_d
	grep sgemm ${file} >> ${TMPFILE}_s
	grep zgemm ${file} >> ${TMPFILE}_z
	grep cgemm ${file} >> ${TMPFILE}_c
done

./Process-dgemm 0 ${TMPFILE}_d
./Process-dgemm 1 ${TMPFILE}_s
./Process-dgemm 2 ${TMPFILE}_z
./Process-dgemm 3 ${TMPFILE}_c

echo "GEMM data created.  Visualize using, for example"
echo "   $ ./heat_dgemm.py -i /tmp/armpl.dgemm"

rm -f ${TMPFILE}_[dszc]
