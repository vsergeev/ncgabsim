CFLAGS=-O3
all:
	gcc $(CFLAGS) -fPIC -shared -o ff.so ff.c
	gcc $(CFLAGS) ff.c -o ff_test
