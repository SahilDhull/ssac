package main;

func ackermann(m int, n int) int {
	if m == 0 {
		return n + 1;
	};

	if n == 0 {
		return ackermann(m-1, 1);
	};

	return ackermann(m-1, ackermann(m, n-1));

	// print m;
	// print n;
	// return 1;
};

func main() {
	print ackermann(3, 2);
};
