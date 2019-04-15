// package main;

// type rect struct {
//     name string;
//     age  int;
//     next *type rect;
// };


// func main(){
// 	var a,b,c,d,e type rect;
// 	a.next, b.next, c.next, d.next = &b, &c, &d, &e;
// 	var an,bn,cn,dn *type rect;
// 	an,bn,cn,dn = a.next, b.next, c.next, d.next;
// 	b.name = "b\n";
// 	b.age = 4;
// 	c.name = "name of c\n";
// 	c.age = 5;
// 	d.name = "name of d\n";
// 	d.age = 6;
// 	e.name = "name of e\n";
// 	e.age = 7;
// 	// e.next = -1;
// 	var s string = an.name;
// 	// print s;
// 	// print an.age;					// 4
// 	// print "\n";
// 	// print bn.age; 				// 5
// 	// print "\n";
// 	// print a.next.next.next.age; 		// 6
// 	// print "\n";
// 	// print a.next.next.next.next.age; 	// 7
// 	var found bool;
// 	var head type *rect;
// 	head = &a;
// 	// found = false;
// 	var t int = 1;
// 	for ; t ; {
// 		// if a.next == nil {
// 		// 	t = 0;
// 		// };
// 		if a.age == 4 {
// 			found = true;
// 			t = 0;
// 		};
// 		a = a.next;
// 	};

// 	if found {
// 		print "Found\n"
// 	} else {
// 		print "Not found\n"
// 	};
// };


package main;


func main() {
	var a [4][4] int;
	var b [4][4] int;
	var res [4][4] int;

	var c int;
	var i int;
	var j int;
	var d int;
	var e int;
	var k int;
	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			scan c;
			a[i][j] = c;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			scan c;
			b[i][j] = c;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			c = 0;
			for k = 0; k < 4; k++ {
				d = a[i][k];
				e = b[k][j];
				c += d * e;
			};
			res[i][j] = c;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			print res[i][j];
			print " ";
		};
		print "\n";
	};
};


// Input
// 1
// 0
// 0
// 0
// 0
// 1
// 0
// 0
// 0
// 0
// 1
// 0
// 0
// 0
// 0
// 1
// 1
// 2
// 3
// 4
// 5
// 6
// 7
// 8
// 9
// 0
// 1
// 2
// 3
// 4
// 5
// 6




