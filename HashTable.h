#ifndef HASHTABLE_H
#define HASHTABLE_H

#include <stdlib.h>

// Constants
#define HASH_TABLE_SIZE 64ull // in MB
#define MB_SIZE 1000000ull

#define FAIL_HIGH 1
#define FAIL_LOW 2
#define EXACT 3

#define MT_STATE_SIZE 624

// Random number generator (built-in is not good enough)
typedef struct {
    unsigned long long mt[MT_STATE_SIZE];
    int index;
} mt_state;

void mt_init(mt_state *state, unsigned long long seed);
unsigned long long mt_rand(mt_state *state);

// Hash table entry
typedef struct {
    unsigned long hash;
    char value;
    char move;
    char flag;
} Entry;

// Hash table
typedef struct {
    Entry* entries;
    unsigned long* zobrist;
    unsigned long long size;
} HashTable;

HashTable* initHashTable();
void freeHashTable(HashTable* table);
Entry* getEntry(HashTable* table, unsigned long hash);
void addEntry(HashTable* table, unsigned long hash, char value, char move, char flag);

#endif // HASHTABLE_H