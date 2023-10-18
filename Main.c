#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "HashTable.c"

#define HEIGHT 6
#define WIDTH 7
#define MAX_STONES 22
#define MOVE_MASK 0b10000000100000001000000010000000100000001
#define BOARD_MASK 0b11111110111111101111111011111110111111101111111

#define SELF_PLAY 0
#define WEAK_SOLVER 0

// A struct to hold the state of the board
// the game board is 6 tall and 7 wide
typedef struct {
    unsigned long long p1;
    unsigned long long p2;
    unsigned long long hash;
    unsigned long long nodes;
} BoardState;

void initBoard(BoardState* board) {
    board->p1 = 0;
    board->p2 = 0;
    board->hash = 0;
    board->nodes = 0;
}

void printBin(unsigned long long n) {
    for (int i = 63; i >= 0; i--) {
        printf("%lld", (n >> i) & 1);
    }
    printf("\n");
}

// print a binary board
void printBinBoard(unsigned long long n) {
    int index = 46;
    for (int col = 0; col < HEIGHT; col++) {
        for (int row = 0; row < WIDTH; row++) {
            printf("%lld", (n >> index) & 1);
            index--;
        }
        index--;
        printf("\n");
    }
    printf("\n");
}

// print a human readable board
void printBoard(BoardState board) {
    int index = 46;
    for (int col = 0; col < HEIGHT; col++) {
        for (int row = 0; row < WIDTH; row++) {
            if (board.p1 >> index & 1 == 1) {
                printf("\033[0;34m O\033[0;37m");
            }
            else if (board.p2 >> index & 1) {
                printf("\033[0;31m O\033[0;37m");
            }
            else {
                printf(" .");
            }

            index--;
        }
        index--;
        printf("\n");
    }
}

// converts the eval to moves to win 
int convertEval(int eval, int player, BoardState* board) {
    if (eval == 0) {
        return 0;
    }

    // use p1 stone count as a proxy for the number of moves played so far
    int retVal = (eval > 0) ? (MAX_STONES - __builtin_popcountll((player) ? board->p2 : board->p1)) - eval
                : -(MAX_STONES - __builtin_popcountll((player) ? board->p2 : board->p1)) - eval + 1;
    return retVal;
}

// return a bitmap of all the winning free spots making an alignment
unsigned long long int computeWinningPosition(unsigned long long position, unsigned long long occupied) {
    // vertical
    unsigned long long r = (position << (WIDTH + 1)) & (position << (2 * (WIDTH + 1))) & (position << (3 * (WIDTH + 1)));

    // horizontal
    unsigned long long p = (position << 1) & (position << 2);
    r |= p & (position << 3);
    r |= p & (position >> 1);
    p = (position >> 1) & (position >> 2);
    r |= p & (position << 1);
    r |= p & (position >> 3);

    // diagonal 1
    p = (position << WIDTH) & (position << (2 * WIDTH));
    r |= p & (position << (3 * WIDTH));
    r |= p & (position >> WIDTH);
    p = (position >> WIDTH) & (position >> (2 * WIDTH));
    r |= p & (position << WIDTH);
    r |= p & (position >> (3 * WIDTH));

    // diagonal 2
    p = (position << (WIDTH + 2)) & (position << (2 * (WIDTH + 2)));
    r |= p & (position << (3 * (WIDTH + 2)));
    r |= p & (position >> (WIDTH + 2));
    p = (position >> (WIDTH + 2)) & (position >> (2 * (WIDTH + 2)));
    r |= p & (position << (WIDTH + 2));
    r |= p & (position >> (3 * (WIDTH + 2)));

    return r & ~occupied & BOARD_MASK;
}

// check if the board is in a winning state
unsigned long long isAligned(BoardState* board, int player) {
    unsigned long long playerPos = (player) ? board->p2 : board->p1;
    unsigned long long occupied = board->p1 | board->p2;
    unsigned long long winningMoves = computeWinningPosition(playerPos, occupied);

    return winningMoves & playerPos;
}

void makeMove(BoardState* board, unsigned long long moves, int player, HashTable* table) {
    if (player) {
        board->p2 = board->p2 ^ moves;
        board->hash = board->hash ^ table->zobrist[__builtin_ctzll(moves) + 64];
    }
    else {
        board->p1 = board->p1 ^ moves;
        board->hash = board->hash ^ table->zobrist[__builtin_ctzll(moves)];
    }
}

// generate the possible moves for this board state
unsigned long long generateMoves(BoardState* board) {
    unsigned long long filledPos = board->p1 | board->p2;
    unsigned long long mask = 0b1111111ull;
    unsigned long long moves = 0;

    for (int i = 0; i < 6; i++) {
        moves = moves | ((filledPos ^ mask) & mask);
        mask = (mask ^ moves) & mask;
        mask = mask << 8;

        if (mask == 0)
            break;
    }

    return moves;
}

// insertion sort the arrays 
void sortArray(char* sortArray, char* valArray, int size) {
    for (int i = 1; i < size; i++) {
        char keySort = sortArray[i];
        char keyVal = valArray[i];
        int j = i - 1;

        while (j >= 0 && sortArray[j] < keySort) {
            sortArray[j + 1] = sortArray[j];
            valArray[j + 1] = valArray[j];
            j--;
        }

        sortArray[j + 1] = keySort;
        valArray[j + 1] = keyVal;
    }
}

// sort the moves by the number of winning positions they create
// use insertion sort as the list is small and mostly sorted
int sortMoves(BoardState* board, unsigned long long moves, char order[], int player) {
    char score[WIDTH];
    unsigned long long moveMasker = MOVE_MASK;
    unsigned long long playerPos = (player) ? board->p2 : board->p1;
    unsigned long long opponentPos = (player) ? board->p1 : board->p2;
    unsigned long long occupied = board->p1 | board->p2;
    unsigned long long move;
    int index = WIDTH;

    // make bit mask that represent the winning moves for both players
    unsigned long long winningMoves = computeWinningPosition(playerPos, occupied);
    unsigned long long opponentWinningPos = computeWinningPosition(opponentPos, occupied);
    unsigned long long nonLossingMoves = opponentWinningPos & moves;

    // there is nothing to do this position is lost since there are two winning moves for the opponent
    if (nonLossingMoves && __builtin_popcountll(nonLossingMoves) > 1) {
        nonLossingMoves = 0;
    } else {
        nonLossingMoves = moves;
    }
    
    // avoid playing below a winning move
    nonLossingMoves = nonLossingMoves & ~(opponentWinningPos >> (WIDTH + 1));

    for (int i = 0; i < WIDTH; i++) {
        move = ((moveMasker << order[i]) & moves);

        if (move & winningMoves) {
            score[i] = 100;
            index--;
            continue;
        }

        if (!move) {
            score[i] = -10;
            index--;
            continue;
        }

        // we should not play moves that lose imidiatly
        if (!(nonLossingMoves & move)) {
            score[i] = -9;
            index--;
            continue;
        }

        // get a count of winning oprotunities for each move this is the default score
        score[i] = __builtin_popcountll(computeWinningPosition(playerPos | move, occupied | move));
    }

    sortArray(score, order, WIDTH);

    return index;
}

int negamax(BoardState* board, int player, int alpha, int beta, HashTable* table) {
    int bestEval = -1000;
    int alphaOrig = alpha;
    int bestMove = -1;
    board->nodes++;

    // generate moves 
    unsigned long long moves = generateMoves(board);

    // check for a draw
    if (!moves)
        return 0;

    // check for a winning move if found store it in the table
    unsigned long long winningMoves = computeWinningPosition((player) ? board->p2 : board->p1, board->p1 | board->p2);
    if (winningMoves & moves) {
        // score is 1 if the player can win with the last stone, 2 if the 
        // player can win with the second last stone etc...
        int score = MAX_STONES - (__builtin_popcountll((player) ? board->p2 : board->p1) + 1);
        addEntry(table, board->hash, player, score, __builtin_ctzll(winningMoves & moves) % (WIDTH + 1), EXACT);
        
        return score;
    }

    // check if the board is in the table
    Entry* entry = getEntry(table, board->hash);
    if (entry != 0) {
        if (entry->flag == EXACT) {
            return entry->value;
        }
        else if (entry->flag == FAIL_LOW) {
            beta = (beta < entry->value) ? beta : entry->value;
        }
        else if (entry->flag == FAIL_HIGH) {
            alpha = (alpha < entry->value) ? alpha : entry->value;
        }
    }

    // check for a cutoff
    if (alpha >= beta)
        return beta;

    unsigned long long move;
    int eval;

    // mask for getting a move from a column
    unsigned long long moveMasker = MOVE_MASK;

    // explore the middle columns first as they are more likely to be good moves
    char exploreOrder[] = { 3, 2, 4, 1, 5, 0, 6 };

    int losingStart = sortMoves(board, moves, exploreOrder, player);

    if (losingStart == 0) {
        // there are no moves that don't lose the game immediately
        // return the score for the opponent winning in the next move
        int score = -(MAX_STONES - (__builtin_popcountll((player) ? board->p1 : board->p2) + 1));
        addEntry(table, board->hash, player, score, __builtin_ctzll(moves & (moveMasker << exploreOrder[0])) % (WIDTH + 1), EXACT);
        return score;
    }

    // loop through moves until there are no more or a cutoff occures
    for (int i = 0; i < losingStart; i++) {
        move = moves & (moveMasker << exploreOrder[i]);

        makeMove(board, move, player, table);

        eval = -negamax(board, !player, -beta, -alpha, table);

        // make move is reversible
        makeMove(board, move, player, table);

        // alpha beta prunning
        if (bestEval < eval) {
            bestEval = eval;
            bestMove = exploreOrder[i];
        }
        alpha = (bestEval < alpha) ? alpha : bestEval;
        if (alpha >= beta) {
            break;
        }
    }

    // set the transposition table flags
    char flag;
    if (bestEval <= alphaOrig)
        flag = FAIL_LOW;
    else if (bestEval >= beta)
        flag = FAIL_HIGH;
    else
        flag = EXACT;


    addEntry(table, board->hash, player, bestEval, bestMove, flag);

    return bestEval;
}

// solve the board
int solve(BoardState* board, int player, HashTable* table, int weak) {
    memset(table->entries, 0, sizeof(Entry) * table->size);
    clock_t start = clock();
    board->nodes = 0;
    int eval = 0;

    // min and max values from the current state
    int min = -(MAX_STONES - __builtin_popcountll(board->p1)); 
    int max = MAX_STONES - __builtin_popcountll(board->p1);

    if (weak) {
        min = -1;
        max = 1;
    }


    while(min < max) {
        int med = min + (max - min ) / 2;
        if (med <= 0 && min / 2 < med)
            med = min / 2;
        else if(med >= 0 && max / 2 > med)
            med = max / 2;

        // use a null depth window search
        eval = negamax(board, player, med, med + 1, table);

        if(eval <= med)
            max = eval;
        else 
            min = eval;

        printf("Window: %d %d\n", min, max);
    }

    printf("Eval: %d\n", convertEval(eval, player, board));
    printf("Nodes: %lld\n", board->nodes);
    printf("Time: %f\n", (double)(clock() - start) / CLOCKS_PER_SEC);

    return min;
}

// play a game with player starting first player is 0 or 1 
int playGame(int player) {
    BoardState board;
    initBoard(&board);
    HashTable* table = initHashTable();
    unsigned long long moveMasker = MOVE_MASK;
    unsigned long long moves;
    unsigned long long move;

    // test p1 win in 18 moves
    board.p1 = 0b00000000000100000000000000010000000000000001000;
    board.p2 = 0b00000000000000000001000000000000000100000000001;

    // get a random hash for the board
    Entry* entry = table->entries + (board.hash % table->size);

    int playing = 1;
    while (playing) {
        moves = generateMoves(&board);

        // check if the game is over
        if (!moves) {
            printBoard(board);
            printf("Draw\n");
            playing = 0;
            break;
        }

        printBoard(board);
        printf(" 6 5 4 3 2 1 0\n");

        // get the computer move
        if (player || SELF_PLAY) {
            solve(&board, player, table, WEAK_SOLVER);
            entry = getEntry(table, board.hash);
            move = moves & (moveMasker << entry->move);
            makeMove(&board, move, player, table);
            printf("Computer plays: %d\n", entry->move);
        }
        else {
            // TODO abstract input validation to a function
            printf("Enter move: ");
            scanf("%d", &move);
            move = moves & (moveMasker << move);
            makeMove(&board, move, player, table);
            
        }

        if (isAligned(&board, player)) {
           printf("\n");
           printBoard(board);
           printf("Player %d wins\n", player + 1);
           playing = 0;
           break;
        }

        // invert the player
        player = !player;
    }

    freeHashTable(table);
}

int runTests() {
    BoardState board;
    initBoard(&board);

    HashTable* table = initHashTable();

    //board.p1 = 0b00111000011000; // check for horizontal win
    //board.p1 = 0b1100000110000011; // check for vertical win
    //board.p1 = 0b00001000000010000000100000000; // check for diagonal win
    //board.p1 = 0b00000000001000001000001000000000000; // check for other diagonal win

    // test p1 win in 6 moves
    //board.p1 = 0b00000100000111000010010010011000001001001001110;
    //board.p2 = 0b000111000101000001001100000100100100110000010001;

    // test p1 win in 14 moves
    board.p1 = 0b00000000000101000000010000010000000001000001001;
    board.p2 = 0b00010000000000000001000000000100000100101000010;

    // test p1 win in 18 moves
    //board.p1 = 0b00000000000100000000000000010000000000000001000;
    //board.p2 = 0b00000000000000000001000000000000000100000000001;

    
    printBoard(board);

    solve(&board, 0, table, WEAK_SOLVER);

    freeHashTable(table);
}

int main(int argc, char* argv[]) {
    runTests();
    playGame(0);
}

