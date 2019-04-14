package main;

<<<<<<< HEAD
func main(){
	var k string;
	var p *string;
	p = &k;
	*p = "ok";
	// *p = 3;
	// print *p;
	// print "\n";
};
=======
type side struct{
	a int;
	b string;
};

type rect struct {
    name string;
    age  int;
    part type side;
};

func f(a type rect) type rect {
	a.name = "\nCOOL\n";
	a.part.b = "\ngggggggg\n";
	return a;
};

func main(){
	var str string = "\n";
	var b type rect;
	b.age = 2;
	b.name = "hey\n";
	b.part.a = 1;
	b.part.b = "Nope\n";
	print b.part.b;
	print b.name;
	print b.age;
	b = f(b);
	print b.name;
	print b.part.b;
};
>>>>>>> 63321e01c6978282ce8a1337319c1977b366b230
