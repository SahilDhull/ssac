package main;

var a int;
var b [5]int;

func main() {
	print a;
	print "\n";
	a = 10;
	print (a);
	print "\n";
	for i := 0; i < 5; i++ {
		b[i] = i + 100;
	};
	for i := 0; i < 5; i++ {
		print (b[i]);
		print "\n";
	};
};
