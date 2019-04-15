<<<<<<< HEAD
package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


func main(){
	// var a *type rect;
	//  a = null;
	//  if a == null{
	//  	print "yooo";
	//  };
	var a,b,c,d,e type rect;
	a.next, b.next, c.next, d.next = &b, &c, &d, &e;
	var an,bn,cn,dn *type rect;
	an,bn,cn,dn = a.next, b.next, c.next, d.next;
	a.age = 8;
	a.name ="kkk\n";
	b.name = "b\n";
	b.age = 4;
	c.name = "name of c\n";
	c.age = 5;
	d.name = "name of d\n";
	d.age = 6;
	e.name = "name of e\n";
	e.age = 7;
	e.next = null;
	var s string = an.name;
	print a.next;
	// print s;
	// print a.age;
	// print an.age;					// 4
	// print "\n";
	// print bn.age; 				// 5
	// print "\n";
	// print a.next.next.next.age; 		// 6
	// print "\n";
	// print a.next.next.next.next.age; 	// 7
	// var found bool;
	// var head *type rect;
	// head = &a;
	// found = false;
	// var t int = 1;
	// for ; t ; {

	// 	// if head.next == null {
	// 	// 	t = 0;
	// 	// };
	// 	if head.age == 5 {
	// 		found = true;
	// 		t = 0;
	// 	};
	// 	head = head.next;
	// };

	// if found {
	// 	print "Found\n";
	// } else {
	// 	print "Not found\n";
	// };
};
=======
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
