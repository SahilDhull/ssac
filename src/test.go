package main;

func f(d *[10]int){
	var c *[10]int = d;
	(*d)[1] = 23;
	(*c)[1] = 90;
	// print *c[1];
	return;
};

func main(){
	var a [10]int;
	var b *[10]int;
	b = &a;
	a[1] = 1;
	print ".....";
	(*b)[1] = 2;
	f(b);
	print a[1], (*b)[1];

};
