#ifndef CONNECT4_H
#define CONNECT4_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include"HashTable.h"

// Structs
typedef struct {
    unsigned long long p1;
    unsigned long long p2;
    unsigned long long nodes;
    unsigned long hash;
} BoardState;

// Function Prototypes
void initBoard(BoardState* board);
void printBin(unsigned long long n);
void printBinBoard(unsigned long long n);
void printBoard(BoardState board);
int getMove();
HashTable* getInitTable();
int convertEval(int eval, int player, BoardState* board);
int findBookMove(char* bookDir, BoardState* board);
unsigned long long computeWinningPosition(unsigned long long position, unsigned long long occupied);
unsigned long long isAligned(BoardState* board, int player);
void makeMove(BoardState* board, unsigned long long move, int player, HashTable* table);
unsigned long long generateMoves(BoardState* board);
unsigned long long getNonLosingMove(BoardState* board, unsigned long long moves, int player);
void sortArray(char* sortArray, char* valArray, int size);
int sortMoves(BoardState* board, unsigned long long moves, char order[], int player, Entry* entry);
int negamax(BoardState* board, int player, int alpha, int beta, HashTable* table);
int solve(BoardState* board, int player, HashTable* table, int weak);
int playGame(int player);
unsigned long long nPlySearch(int n, BoardState* board, int player, HashTable* table);
int computeBookRecursive(char* bookDir, BoardState* board, int player, HashTable* table, int depth);
void computeBook(char* bookDir);
int benchmark(char* filename);

#endif // CONNECT4_H