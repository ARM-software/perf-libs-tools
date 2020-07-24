CFLAGS=-O3 -Wno-pointer-to-int-cast
OMPFLAG=-fopenmp

CC=gcc
#CC=armclang

all: Makefile libarmpl-logger.so libarmpl-summarylog.so libarmpl_mp-summarylog.so src/PROTOTYPES tools

libarmpl-logger.so: preload-gen.c src/logging.c src/PROTOTYPES
	cd src && ${CC} -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-gen.c logging.c -ldl -DLOGGING

libarmpl-summarylog.so: preload-sumgen.c src/summary.c src/PROTOTYPES
	cd src && ${CC} -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

libarmpl_mp-summarylog.so: preload-sumgen.c src/summary.c src/PROTOTYPES
	cd src && ${CC} -fPIC ${CFLAGS} ${OMPFLAG} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-gen.c: src/makepreload.py src/PROTOTYPES
	cd src && python makepreload.py 

preload-sumgen.c: src/makepreload-post.py src/PROTOTYPES
	cd src && python makepreload-post.py

tools: tools/Process-dgemm

tools/Process-dgemm:
	cd tools ; ${CC} -o Process-dgemm process-dgemm.c -O2 -lm

clean:
	rm -f src/preload-gen.c src/preload-sumgen.c
	rm -f lib/libarmpl-logger.so lib/libarmpl-summarylog.so lib/libarmpl_mp-summarylog.so
	rm -f tools/Process-dgemm
