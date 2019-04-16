package main;

type node struct {
	val int;
	next *type node;
};

func main() {
	var s type node;
	var n1 *type node;
	var n2 **type node;
	s.val = 23;
	n1 = &s;
	n2 = &n1;
	print n1.val;
	print n2.val;
};