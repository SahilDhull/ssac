package main;

type node struct {
    val  int;
    next *type node;
};

func main() {
	var a type node;
	a.val = 1;
	g:=a;
	print g.val;
};