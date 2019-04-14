package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


func main(){
	var a [2]type rect;
	a[0].next = &a[1];
	a[1].age = 10;
	print a[0].next.age;
};
