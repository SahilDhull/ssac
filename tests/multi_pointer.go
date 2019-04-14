package main;

func main(){
	var p1 *int;
	var p2 **int;
	var p3 ***int;
	var a int = 5;
	p1 = &a;
	p2 = &p1;
	p3 = &p2;
	print *p1;
	print "\n";
	print **p2;
	print "\n";
	print ***p3;
	print "\n";
	*p1 = 1;
	print ***p3;
	print "\n";
	print a;
	print "\n";
	a = 77;
	print **p2;
	**p2 = *p1 + ***p3;
	***p3 += 5;
	print "\n";
	print ***p3;
	print "\n";
};
