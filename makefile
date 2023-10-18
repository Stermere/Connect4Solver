all: connect4

connect4: Main.c
	gcc Main.c -O3 -o TheConnector

clean:
	rm -f TheConnector