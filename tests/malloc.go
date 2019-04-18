package main;

type node struct {
	val int;
	l *type node;
	r *type node;
};

func main() {
	var a int = 5;
	var b *int = malloc(4);
	*b = 5;
	var c *int;
	c = malloc(4);
	*c = 7;
	print *c,"\n",*b,"\n";
	var head,tail *type node;
	head = malloc(12);
	tail = malloc(12);
	head.val = 1;
	head.l = tail;
	tail.val = 23;
	print head.l.val;
};
