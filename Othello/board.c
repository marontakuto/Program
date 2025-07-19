#include <stdio.h>
#include "board.h"

static const int dir[8][2] = {
    {-1, -1}, {-1, 0}, {-1, 1}, 
    { 0, -1}, { 0, 1}, 
    { 1, -1}, { 1, 0}, { 1, 1}
};

void init_board(int board[8][8]) {
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8; j++)
            board[i][j] = EMPTY;

    board[3][3] = WHITE;
    board[3][4] = BLACK;
    board[4][3] = BLACK;
    board[4][4] = WHITE;
}

void print_board(int board[8][8]) {
    printf("  ");
    for (int i = 0; i < 8; i++) printf("%d ", i);
    printf("\n");

    for (int i = 0; i < 8; i++) {
        printf("%d ", i);
        for (int j = 0; j < 8; j++) {
            if (board[i][j] == BLACK) printf("œ ");
            else if (board[i][j] == WHITE) printf("› ");
            else printf(". ");
        }
        printf("\n");
    }
}

int is_valid_move(int board[8][8], int row, int col, int color) {
    if (board[row][col] != EMPTY) return 0;

    for (int d = 0; d < 8; d++) {
        int x = row + dir[d][0];
        int y = col + dir[d][1];
        int found_opponent = 0;

        while (x >= 0 && x < 8 && y >= 0 && y < 8) {
            if (board[x][y] == -color) {
                found_opponent = 1;
            }
            else if (board[x][y] == color && found_opponent) {
                return 1;
            }
            else {
                break;
            }
            x += dir[d][0];
            y += dir[d][1];
        }
    }
    return 0;
}

int has_valid_move(int board[8][8], int color) {
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8; j++)
            if (is_valid_move(board, i, j, color))
                return 1;
    return 0;
}

void place_disc(int board[8][8], int row, int col, int color) {
    board[row][col] = color;

    for (int d = 0; d < 8; d++) {
        int x = row + dir[d][0];
        int y = col + dir[d][1];
        int to_flip[8][2], flip_count = 0;

        while (x >= 0 && x < 8 && y >= 0 && y < 8 && board[x][y] == -color) {
            to_flip[flip_count][0] = x;
            to_flip[flip_count][1] = y;
            flip_count++;
            x += dir[d][0];
            y += dir[d][1];
        }

        if (x >= 0 && x < 8 && y >= 0 && y < 8 && board[x][y] == color) {
            for (int i = 0; i < flip_count; i++)
                board[to_flip[i][0]][to_flip[i][1]] = color;
        }
    }
}

int is_game_over(int board[8][8]) {
    return !has_valid_move(board, BLACK) && !has_valid_move(board, WHITE);
}

int count_discs(int board[8][8], int color) {
    int count = 0;
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8; j++)
            if (board[i][j] == color)
                count++;
    return count;
}

int count_flippable(int board[8][8], int row, int col, int color) {
    if (board[row][col] != EMPTY) return 0;

    int flip_count = 0;

    for (int d = 0; d < 8; d++) {
        int x = row + dir[d][0];
        int y = col + dir[d][1];
        int count = 0;

        while (x >= 0 && x < 8 && y >= 0 && y < 8 && board[x][y] == -color) {
            count++;
            x += dir[d][0];
            y += dir[d][1];
        }

        if (count > 0 && x >= 0 && x < 8 && y >= 0 && y < 8 && board[x][y] == color) {
            flip_count += count;
        }
    }

    return flip_count;
}

void apply_move(int board[8][8], int row, int col, int color) {
    place_disc(board, row, col, color);
}

int count_stones(int board[8][8], int color) {
    return count_discs(board, color);
}
