package main;

func fibo(a int) int {
	if a == 0 {
		return 1;
	};
	if a == 1 {
		return 1;
	};
	return fibo(a-1)+fibo(a-2);
};

func main() {
	for i:=0;i<15;i++{
		print fibo(i),"  ";
	};
	print "\n";
};