CFLAGS=-O3 -Wno-pointer-to-int-cast

all: Makefile libarmpl-summarylog.so libarmpl-math-summarylog.so libgeneric-summarylog.so tools

## DEPRECATED LOGGING TOOL
# libarmpl-logger.so: preload-gen.c src/logging.c src/PROTOTYPES
# 	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-gen.c logging.c -ldl -DLOGGING
# preload-gen.c: src/makepreload.py 
# 	cd src && python makepreload.py

## ARMPL Tracer
libarmpl-summarylog.so: preload-sumgen.c src/summary.c
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-sumgen.c: src/makepreload-post.py 
	cd src && python makepreload-post.py -i "PROTOTYPES"

## ARMPL Tracer with Math Library
libarmpl-math-summarylog.so: preload-sumgen-math.c src/summary.c
	cd src && gcc -fPIC ${CFLAGS} -Wno-incompatible-library-redeclaration -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-sumgen-math.c: src/makepreload-post.py 
	cd src && python makepreload-post.py -i "PROTOTYPES_MATH"

## Generic BLAS Tracer
libgeneric-summarylog.so: preload-sumgen-generic.c src/summary.c
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-sumgen-generic.c: src/makepreload-post.py 
	cd src && python makepreload-post.py -i "PROTOTYPES_GENERIC"

## CBLAS Tracer - In Progress
libcblas-summarylog.so: preload-sumgen-cblas.c src/summary.c
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl


tools: tools/Process-dgemm

tools/Process-dgemm:
	cd tools ; gcc -o Process-dgemm process-dgemm.c -O2 -lm

clean:
	rm -f src/preload-gen.c src/preload-sumgen.c
	rm -f lib/*.so
	rm -f tools/Process-dgemm
