package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


func main(){
	var a [5]type rect;
	var k string = "----->>>>>>>>>>>";
	a[0].next = &a[1];
	a[1].next = &a[2];
	a[2].next = &a[3];
	a[3].next = &a[4];
	// a[0].age = 23;
	var g string = "............";
	a[2].age = 34;
	// var f string = ",,,,,,,,,,,,"; 
	// a[2].age = 35;
	// a[2].name = "ankit apna bhai hai\n";
	// a[3].age = 67;
	// a[4].age = 89;
	var s string = "-----------------";
	print a[1].age;
	print a[1].next.age;
	// print a[0].name;
};
