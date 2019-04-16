package main;

func g(e *[10]int){
	(*e)[1] = 45;
	return;
};

func f(d *[10]int){
	(*d)[1] = 23;
	g(d);
	return;
};

func main(){
	var a [10]int;
	var b *[10]int;
	b = &a;
	a[1] = 1;
	(*b)[1] = 2;
	f(b);
	print "a[1] = ",a[1],"\n", "(*b)[i] = ", (*b)[1],"\n";

};
