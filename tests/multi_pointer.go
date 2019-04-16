package main;

func main(){
	var p1 *int;
	var p2 **int;
	var p3 ***int;
	var a int = 5;
	p1, p2, p3 = &a, &p1, &p2;
	print *p1;
	print "\n";
	print **p2;
	print "\n";
	print ***p3;
	print "\n";
	*p1 = 1;
	print ***p3,"\n",a,"\n";
	a = 77;
	print **p2,"\n";
	**p2 = *p1 + ***p3;
	***p3 += 5;
	print ***p3,"\n";
	var g1 *string;
	var g2 **string;
	var k string = "hello world!\n";
	g1 = &k;
	g2 = &g1;
	print *g1;
};
