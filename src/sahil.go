package main;

func main() {
	var a,b *int;
	var c int = 7;
	a = &c;
	print *a;
	var e [10]int;
	var d *[10]int;
	d = &e;
	e[1] = 1;
	print (*d)[1];
};
