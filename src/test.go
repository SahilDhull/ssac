package main;

type node struct {
	val int;
	l *type node;
	// r *type node;
};

func f(head *type node){
	if head==null{
		return;
	};
	f(head.l);
	print head.val;
};

func main(){
	var a[5]type node;
	for i:=0;i<4;i++{
		a[i].val = i;
		a[i].l = &a[i+1];
	};
	a[4].l = null;

	head := &a[0];

	// print head.l.val;
	f(head);
};
