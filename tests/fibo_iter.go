package main;

func fibo_iter(n int) {
	a := 0;
	b := 1;
	for i := 0; i < n; i++ {
		print a;
		print ",";
		tmp := a + b;
		a = b;
		b = tmp;
	};
};

func main() {
	a := 0;
	print "First N Fibonacci No\n";
	print "Enter N : ";
	scan a;
	fibo_iter(a);
};
