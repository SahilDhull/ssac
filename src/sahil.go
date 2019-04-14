package main;

type side struct{
	len int;
	wid int;
};

type rect struct {
    name string;
    age  int;
    next *type side;
};


func main(){
	var a type rect;
	var b type side;
	a.next = &b;
	b.len = 3;
	print a.next.len;
	// a[0].next = &a[1];
	// a[1].age = 1;
	// print a[0].next.age;
};
