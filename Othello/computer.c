#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "board.h"
#include "computer.h"

static const int weights[8][8] = {
    {100, -20, 10, 5, 5, 10, -20, 100},
    {-20, -50, -2, -2, -2, -2, -50, -20},
    {10, -2, 0, 0, 0, 0, -2, 10},
    {5, -2, 0, 0, 0, 0, -2, 5},
    {5, -2, 0, 0, 0, 0, -2, 5},
    {10, -2, 0, 0, 0, 0, -2, 10},
    {-20, -50, -2, -2, -2, -2, -50, -20},
    {100, -20, 10, 5, 5, 10, -20, 100}
};

void get_computer_move(int board[8][8], int color, int* row, int* col, Strategy strategy) {
    int valid_moves[60][2];
    int count = 0;

    for (int r = 0; r < 8; r++) {
        for (int c = 0; c < 8; c++) {
            if (is_valid_move(board, r, c, color)) {
                valid_moves[count][0] = r;
                valid_moves[count][1] = c;
                count++;
            }
        }
    }

    if (count == 0) {
        *row = -1;
        *col = -1;
        return;
    }

    int best_index = 0;

    if (strategy == RANDOM) {
        srand((unsigned int)time(NULL));
        best_index = rand() % count;
    }
    else if (strategy == MAX_FLIP) {
        int max_flip = -1;
        for (int i = 0; i < count; i++) {
            int r = valid_moves[i][0];
            int c = valid_moves[i][1];
            int flipped = count_flippable(board, r, c, color);
            if (flipped > max_flip) {
                max_flip = flipped;
                best_index = i;
            }
        }
    }
    else if (strategy == WEIGHTED) {
        int best_score = -1000;
        for (int i = 0; i < count; i++) {
            int r = valid_moves[i][0];
            int c = valid_moves[i][1];
            int score = weights[r][c];
            if (score > best_score) {
                best_score = score;
                best_index = i;
            }
        }
    }

    *row = valid_moves[best_index][0];
    *col = valid_moves[best_index][1];
}
