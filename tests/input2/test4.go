package main;

import (
	"fmt";
	"strings";
);

func main() {
	// Create a tic-tac-toe board.
	var game [3][3] string_t; 

	// The players take turns.
	game[0][0] = "X";
	game[2][2] = "O";
	game[2][0] = "X";
	game[1][0] = "O";
	game[0][2] = "X";

	printBoard(game);
};

func printBoard(s  string_t) {
	for i := 0; i < len(s); i++ {
		f(i);
	};
};
