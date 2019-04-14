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
	b.name = "b\n";
	b.age = 4;
	c.name = "name of c\n";
	c.age = 5;
	d.name = "name of d\n";
	d.age = 6;
	e.name = "name of e\n";
	e.age = 7;
	var s string = an.name;
	print s;
	print an.age;					// 4
	print "\n";
	print bn.age; 				// 5
	print "\n";
	print a.next.next.next.age; 		// 6
	print "\n";
	print a.next.next.next.next.age; 	// 7
};
