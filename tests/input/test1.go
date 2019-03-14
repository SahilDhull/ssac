// struct
package math;

import "fmt";

type side struct {
	l int;
	k int;
};
	
type rect struct {
    name string;
    age  int;
    next *type side;
};

func main(){
	var b type rect;
	var k type side;
	// var d int;
	// d =1;
	b.next = &k;
	// b.age = 1;
	b.next.l=1;
	b.next.k = 1;
	var c int;
	c = 1;
};
