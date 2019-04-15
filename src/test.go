package main;

import "fmt";

func main() {
	var c,d int;
	var a [2][2][2][2][2][2]int;
	a[1][1][1][1][1][1] = 1;
	a[1][1][1][1][1][1] = 2;
	c = a[1][1][1][1][1][1];
	d = a[1][1][1][1][1][1];
	print d;
};
