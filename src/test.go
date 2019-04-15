package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


// func main(){
// 	var a,b type rect;
// 	a.next = &b;
// 	var an *type rect;
// 	an= a.next;
// 	b.name = "name of b\n";
// 	b.age = 4;
// 	var s string = an.name;
// 	print an.name;
// 	print "\n";
// 	print s;
// 	print "\n";
// 	print an.age;					// 4
// 	print "\n";
// };


func main(){
	var a [3]type rect;
	// a[0].next = &a[1];
	a[1].next = &a[2];
	a[2].age = 1;
	a[1].age = 4;
	var c int = a[0].next.age;
	print c;
};