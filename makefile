CC = gcc
CFLAGS = -O3

all: connect4 connect4dll

connect4: Main.c Main.h HashTable.o
	$(CC) $(CFLAGS) Main.c hashtable.o -o TheConnector

connect4dll: Main.c Main.h HashTable.o
	$(CC) $(CFLAGS) -shared -o TheConnector.dll Main.c HashTable.o

HashTable.o: HashTable.c HashTable.h
	$(CC) $(CFLAGS) -c HashTable.c

clean:
	rm -f TheConnector TheConnector.dll HashTable.o