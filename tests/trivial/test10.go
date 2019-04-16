// high level declarations

package math;

import "fmt";

type rect struct {
    name string;
    age  int;
};

func main(){
	var b [2]*int;
	var d *int;
	var a [2] type rect;
	var c [2][2] type rect;
	var e int;
	b[0] = &e;
	b[1] = d;
	a[1].age=1;
};