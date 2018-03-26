CFLAGS=-O3 -Wno-pointer-to-int-cast

all: Makefile libarmpl-logger.so libarmpl-summarylog.so src/PROTOTYPES tools

libarmpl-logger.so: preload-gen.c src/logging.c src/PROTOTYPES
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-gen.c logging.c -ldl -DLOGGING

libarmpl-summarylog.so: preload-sumgen.c src/summary.c src/PROTOTYPES
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-gen.c: src/makepreload.py src/PROTOTYPES
	cd src && python makepreload.py 

preload-sumgen.c: src/makepreload-post.py src/PROTOTYPES
	cd src && python makepreload-post.py

tools: tools/Process-dgemm

tools/Process-dgemm:
	cd tools ; gcc -o Process-dgemm process-dgemm.c -O2 -lm

clean:
	rm -f src/preload-gen.c src/preload-sumgen.c
	rm -f lib/libarmpl-logger.so lib/libarmpl-summarylog.so
	rm -f tools/Process-dgemm
