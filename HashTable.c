#include <stdlib.h>

#define HASH_TABLE_SIZE 64ull // in MB
#define MB_SIZE 1000000ull

#define FAIL_HIGH 1
#define FAIL_LOW 2
#define EXACT 3

#define MT_STATE_SIZE 624

// Random number generator (built in is not good enough)
struct mt_state {
    unsigned long long mt[MT_STATE_SIZE];
    int index;
};

void mt_init(struct mt_state *state, unsigned long long seed) {
    state->mt[0] = seed;
    for (int i = 1; i < MT_STATE_SIZE; ++i) {
        state->mt[i] = 0xFFFFFFFFFFFFFFFFull & (6364136223846793005ull * (state->mt[i - 1] ^ (state->mt[i - 1] >> 62)) + i);
    }
    state->index = MT_STATE_SIZE;
}

// Generate a 64-bit random number using the Mersenne Twister algorithm
unsigned long long mt_rand(struct mt_state *state) {
    if (state->index >= MT_STATE_SIZE) {
        for (int i = 0; i < MT_STATE_SIZE; ++i) {
            unsigned long long y = (state->mt[i] & 0x8000000000000000ull) + (state->mt[(i + 1) % MT_STATE_SIZE] & 0x7FFFFFFFFFFFFFFFull);
            state->mt[i] = state->mt[(i + 397) % MT_STATE_SIZE] ^ (y >> 1);
            if (y % 2 != 0) {
                state->mt[i] ^= 0x9D2C5680u;
            }
        }
        state->index = 0;
    }

    unsigned long long y = state->mt[state->index];
    y ^= (y >> 29) & 0x5555555555555555ull;
    y ^= (y << 17) & 0x71D67FFFEDA60000ull;
    y ^= (y << 37) & 0xFFF7EEE000000000ull;
    y ^= y >> 43;

    state->index++;

    return y;
}

typedef struct {
    unsigned long hash;
    char value;
    char move;
    char flag;
} Entry;

typedef struct {
    Entry* entries;
    unsigned long* zobrist;
    unsigned long long size;
} HashTable;


HashTable* initHashTable() {
    HashTable* table = malloc(sizeof(HashTable));
    table->size = ((HASH_TABLE_SIZE * MB_SIZE) / sizeof(Entry));
    table->entries = malloc(table->size * sizeof(Entry));

    // Init the Zobrist hashing table
    table->zobrist = malloc(sizeof(unsigned long) * 64 * 2);
    struct mt_state state;
    mt_init(&state, 0xdeadbeef);
    for (int i = 0; i < 64 * 2; i++) {
        table->zobrist[i] = (unsigned long)mt_rand(&state);
    }

    return table;
}

void freeHashTable(HashTable* table) {
    free(table->entries);
    free(table->zobrist);
    free(table);
}

Entry* getEntry(HashTable* table, unsigned long hash) {
    if (table->entries[hash % table->size].hash == hash) {
        return &table->entries[hash % table->size];
    }
    return 0;

}

void addEntry(HashTable* table, unsigned long hash, char value, char move, char flag) {
    Entry* entry = table->entries + (hash % table->size);
    entry->hash = hash;
    entry->value = value;
    entry->move = move;
    entry->flag = flag;
}

