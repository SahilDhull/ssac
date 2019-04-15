package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


func main(){
	var a,b,c,d,e type rect;
	a.next, b.next, c.next, d.next = &b, &c, &d, &e;
	var an,bn,cn,dn *type rect;
	an,bn,cn,dn = a.next, b.next, c.next, d.next;
	b.name = "name of b\n";
	b.age = 4;
	c.name = "name of c\n";
	c.age = 5;
	d.name = "name of d\n";
	d.age = 6;
	e.name = "name of e\n";
	e.age = 7;
	print a.next.age;						// 4
	print "\n",	a.next.name;				// name of b
	print an.age;							// 4
	print "\n",an.next.name;				// name of c
	print bn.name; 							// name of c
	print a.next.next.next.name; 			// name of d
	print a.next.next.next.next.age; 		// 7
	print "\n";
};
