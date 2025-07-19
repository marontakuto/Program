#pragma once
#ifndef BOARD_H
#define BOARD_H

#define BLACK 1
#define WHITE -1
#define EMPTY 0

void init_board(int board[8][8]);
void print_board(int board[8][8]);
int is_valid_move(int board[8][8], int row, int col, int color);
int has_valid_move(int board[8][8], int color);
void place_disc(int board[8][8], int row, int col, int color);
int is_game_over(int board[8][8]);
int count_discs(int board[8][8], int color);
int count_flippable(int board[8][8], int row, int col, int color);
void apply_move(int board[8][8], int row, int col, int color);
int count_stones(int board[8][8], int color);

#endif
