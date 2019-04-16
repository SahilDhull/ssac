package main;

func f(d *[10]int){
	(*d)[1] = 23;
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
