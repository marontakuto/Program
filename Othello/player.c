#include <stdio.h>
#include "board.h"
#include "player.h"

void get_player_move(int board[8][8], int color, int* row, int* col) {
    while (1) {
        printf("���Ȃ��̔Ԃł��i�s ��j> ");
        scanf_s("%d %d", row, col);

        if (*row >= 0 && *row < 8 && *col >= 0 && *col < 8) {
            if (is_valid_move(board, *row, *col, color)) {
                break;
            }
            else {
                printf("���̈ʒu�ɂ͒u���܂���B\n");
            }
        }
        else {
            printf("�͈͊O�̓��͂ł��B\n");
        }
    }
}
