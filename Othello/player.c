#include <stdio.h>
#include "board.h"
#include "player.h"

void get_player_move(int board[8][8], int color, int* row, int* col) {
    while (1) {
        printf("あなたの番です（行 列）> ");
        scanf_s("%d %d", row, col);

        if (*row >= 0 && *row < 8 && *col >= 0 && *col < 8) {
            if (is_valid_move(board, *row, *col, color)) {
                break;
            }
            else {
                printf("その位置には置けません。\n");
            }
        }
        else {
            printf("範囲外の入力です。\n");
        }
    }
}
