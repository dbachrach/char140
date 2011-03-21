CC=gcc
OMP_FLAG=-fopenmp
CFLAGS=-O2 -std=gnu99 -m64
LIBS=-L/usr/lib -lm -lssl

all: omp

omp: collider.c
	$(CC) $(CFLAGS) $(OMP_FLAG) collider.c -o collider $(LIBS)
