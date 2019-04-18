package main;

func arglist(a int, b string, c [5]int, d [3][4]int, e int, f int, g int, h int) ([5]int,[3][4]int){
	print a , "   ",b,"   ",c[3],"   ",d[1][2],"   ",e,"   ",f,"   ",g,"   ",h,"\n";
	c[3] = 99;
	d[2][3] = 105;
	return c,d;
};

func main() {
	var a [5]int;
	a[3] = 54;
	var b [3][4]int;
	b[1][2] = 23;
	a,b = arglist(1, "Okay", a, b, 5, 6, 7, 8);
	print a[3]," ",b[2][3],"\n";
};
