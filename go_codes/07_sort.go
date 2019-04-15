package main;
<<<<<<< HEAD

import "fmt";

func main() {
	var b [6]int;
=======

func main() {
	var b [5]int;
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
	b[0] = 7;
	b[1] = 5;
	b[2] = 9;
	b[3] = 2;
	b[4] = 6;

<<<<<<< HEAD
	for i = 0; i < 5; i = i + 1 {
		for j = 0; j < 4; j = j + 1 {
			if b[j] > b[j+1] {
				c = b[j];
=======
	for i := 0; i < 5; i++ {
		for j := 0; j < 4; j++ {
			if b[j] > b[j+1] {
				c := b[j];
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
				b[j] = b[j+1];
				b[j+1] = c;
			};
		};
	};

	for i := 0; i < 5; i = i + 1 {
		print b[i];
<<<<<<< HEAD
		print " ";
	};
	print "\n";
=======
		print "\n";
	};
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
};
