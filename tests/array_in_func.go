package main;

func f(b [2][3]int) ([2][3]int) {
	b[1][2]= 1;
	var c int = b[1][2];
	return b;
};

func main(){
	var a [2][3]int;
	a[1][2] = 3;
	var c1 int = a[1][2];
	print c1,"\n";
	a = f(a);
	print c1,"\n";
	var c2 int = a[1][2];
	print c2,"\n";
};
