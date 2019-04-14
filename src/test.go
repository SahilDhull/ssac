package main;

func ackermann(m int, n int) int {
	if m == 0 {
		return n + 1;
	};

	if n == 0 && m > 0 {
		return ackermann(m-1, 1);
	};

	return ackermann(m-1, ackermann(m, n-1));
};

func main() {
	print ackermann(3, 4);
};


// func main(){
// 	var a int = 3;
// 	var b int = -2;
// 	if a < 0 && b < 0 {
// 		print a;
// 	};
// };
