package main;

type node struct {
	val int;
	l *type node;
	r *type node;
};

func bst(head *type node) {
	if head == null {
		return;
	};
	bst(head.l);
	print head.val;
	bst(head.r);
};

func main() {

	var a1 type node;
	a1.val = 1;
	var a2 type node;
	a2.val = 2;
	var a3 type node;
	a3.val = 3;
	var a4 type node;
	a4.val = 4;
	var a5 type node;
	a5.val = 5;

	head := &a1;

	a1.l = &a2;
	a1.r = &a3;
	a2.l = &a4;
	a2.r = &a5;
	a3.l = null;
	a3.r = null;
	a4.l = null;
	a4.r = null;
	a5.l = null;
	a5.r = null;

	bst(head);
};
