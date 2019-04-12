package main;

func f(b [2]int) int {
	var c int = b[1];
	// print c;
	return c;
};

func main(){
	var a [2]int;
	a[0] = 2;
	a[1]=2+a[0];
	var b int = f(a);
	print b;
};