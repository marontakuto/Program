#pragma once
#ifndef COMPUTER_H
#define COMPUTER_H

typedef enum {
    RANDOM,
    MAX_FLIP,
    WEIGHTED
} Strategy;

void get_computer_move(int board[8][8], int color, int* row, int* col, Strategy strategy);

#endif
