package main;

func f(a[5]int, b [2][3]int,j string) (string,[5]int,[2][3]int) {
	b[1][2]= 1;
	a[2] = 99;
	return "Hello World\n",a,b;
};

func main(){
	var b [2][3]int;
	var a [5]int;
	a[2] = 23;
	b[1][2] = 34;
	var s,k string;
	print "Enter a string : ";
	scan k;
	s,a,b = f(a,b,k);
	print s,a[2],"\n",b[1][2];
};

