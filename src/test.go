package main;

func main(){
	var a [2]string;
	a[0] = "shubham\n";
	var b string;
	b = a[0];
	a[1] = a[0];
	print a[0],b,a[1];
};