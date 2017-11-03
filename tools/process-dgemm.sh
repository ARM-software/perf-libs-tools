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

TMPFILE=/tmp/.inp-$USER
grep dgemm $* |wc -l > $TMPFILE
for file in $*
do	
	#ls -l $TMPFILE
	grep dgemm $file |awk '{print $2 " " $4 " " $6 " " $8 " " $9 " " $10 " " $11 " " $12 " " $13 " " $14 " " $15 " " $16}' >> $TMPFILE
	#ls -l $TMPFILE
	#head $TMPFILE 
done

./Process-dgemm

rm -f $TMPFILE
