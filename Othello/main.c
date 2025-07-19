#include <stdio.h>
#include <stdlib.h>
#include "board.h"
#include "computer.h"

static void print_menu() {
    printf("オセロ：人間 vs コンピュータ\n");
    printf("コンピュータの戦略を選んでください:\n");
    printf("1. ランダム\n");
    printf("2. 最大取得\n");
    printf("3. 重み評価\n");
    printf("番号を入力してください（1~3）: ");
}

int main() {
    int board[8][8];
    int turn = BLACK;  // 黒（人間）先手
    Strategy strategy;
    int input;

    init_board(board);
    print_board(board);

    // 戦略選択
    print_menu();
    scanf_s("%d", &input);
    switch (input) {
    case 1:
        strategy = RANDOM;
        break;
    case 2:
        strategy = MAX_FLIP;
        break;
    case 3:
        strategy = WEIGHTED;
        break;
    default:
        printf("無効な入力です。ランダムに設定します。\n");
        strategy = RANDOM; 
        break;
    }

    while (!is_game_over(board)) {
        printf("\n現在の手番: %s\n", (turn == BLACK) ? "人間（黒）" : "コンピュータ（白）");

        if (has_valid_move(board, turn)) {
            int row, col;
            if (turn == BLACK) {
                // 人間の入力
                printf("行（0~7）を入力: ");
                scanf_s("%d", &row);
                printf("列（0~7）を入力: ");
                scanf_s("%d", &col);
                if (is_valid_move(board, row, col, turn)) {
                    apply_move(board, row, col, turn);
                }
                else {
                    printf("無効な手です。もう一度。\n");
                    continue;
                }
            }
            else {
                // コンピュータの手
                get_computer_move(board, turn, &row, &col, strategy);
                if (row != -1 && col != -1) {
                    printf("コンピュータが (%d, %d) に置きます。\n", row, col);
                    apply_move(board, row, col, turn);
                }
            }
            print_board(board);
        }
        else {
            printf("合法手がありません。スキップします。\n");
        }

        // ターン交代
        turn = (turn == BLACK) ? WHITE : BLACK;
    }

    // 結果表示
    int black_score = count_stones(board, BLACK);
    int white_score = count_stones(board, WHITE);
    printf("ゲーム終了\n");
    printf("黒: %d, 白: %d\n", black_score, white_score);
    if (black_score > white_score) {
        printf("人間（黒）の勝ち！\n");
    }
    else if (black_score < white_score) {
        printf("コンピュータ（白）の勝ち！\n");
    }
    else {
        printf("引き分け！\n");
    }

    return 0;
}
