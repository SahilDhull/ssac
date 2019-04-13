package main;

func f(a[5]int, b [2][3]int) ([5]int,[2][3]int) {
	b[1][2]= 1;
	a[2] = 99;
	return a,b;
};

func main(){
	var b [2][3]int;
	var a [5]int;
	a[2] = 23;
	b[1][2] = 34;
	a,b = f(a,b);
	var c,d int = a[2],b[1][2];
	print c;
	print d;
};

