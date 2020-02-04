CFLAGS=-O3 -Wno-pointer-to-int-cast

all: Makefile libarmpl-logger.so libarmpl-summarylog.so libsci-summarylog.so  src/PROTOTYPES tools

libarmpl-logger.so: preload-gen.c src/logging.c src/PROTOTYPES
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-gen.c logging.c -ldl -DLOGGING

libarmpl-summarylog.so: preload-sumgen.c src/summary.c src/PROTOTYPES
	cd src && gcc -fPIC ${CFLAGS} -shared -o ../lib/$@ preload-sumgen.c summary.c -ldl

libsci-summarylog.so: preload-sumgen-libsci.c src/summary.c src/PROTOTYPES 
	cd src && gcc -fPIC ${CFLAGS} -shared -L/opt/cray/pe/libsci/18.12.1/CRAY/8.6/aarch64/lib/ -lsci_cray_mp -o ../lib/$@ preload-sumgen.c summary.c -ldl

preload-gen.c: src/makepreload.py src/PROTOTYPES
	cd src && python makepreload.py

preload-sumgen.c: src/makepreload-post.py src/PROTOTYPES
	cd src && python makepreload-post.py

preload-sumgen-libsci.c: src/makepreloadlibsci-post.py src/PROTOTYPES
	cd src && python makepreloadlibsci-post.py

tools: tools/Process-dgemm

tools/Process-dgemm:
	cd tools ; gcc -o Process-dgemm process-dgemm.c -O2 -lm

clean:
	rm -f src/preload-gen.c src/preload-sumgen.c
	rm -f lib/libarmpl-logger.so lib/libarmpl-summarylog.so
	rm -f tools/Process-dgemm
