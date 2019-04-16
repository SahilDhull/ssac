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
	print a.next.len,"\n";
	a.next.len = 1;
	print b.len;
};
