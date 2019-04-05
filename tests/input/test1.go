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
	b.next = &k;
	b.next.l=1;
	b.next.k = 1;
	var c int;
	c = 1;
};
