package main;

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
