package main;

func f(a int) int{
	if a==1 {
		return 1;
	};
	var b int = f(a-1);
	return a*b;
};

func main() {
	var a int;
	scan a;
	print f(a);
};