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
	print head.val," ";
	bst(head.r);
	return;
};

func search(head *type node, c int){
	if head==null{
		print c," : Not found\n";
		return;
	};
	if c<head.val{
		search(head.l,c);
	}
	else if c>head.val{
		search(head.r,c);
	}
	else{
		print c," : Key found\n";
	}
	return;
}

func insert(head *type node, c int){
	if head == null{
		head.val=c;
		head.l = null;
		head.r = null;
	};
	if c<head.val{
		insert(head.l,c);
	}
	else if c>head.val{
		insert(head.r,c);
	}
	else{
		print c," : This Key already exists\n";
	}
	return;
};

func main() {

	var a [5]type node;
	var head *type node;

	for i:=0;i<5;i++{
		// a[i].val = i;
		a[i].l = null;
		a[i].r = null;
	};
	a[0].val = 3;
	a[1].val = 2;
	a[2].val = 1;
	a[3].val = 4;
	a[4].val = 5;
	a[0].l = &a[2];
	a[0].r = &a[4];
	a[2].r = &a[1];
	a[4].l = &a[3];

	head = &a[0];
	print "Inorder of BST:\n";
	bst(head);
	print "\nEnter Element to find: ";
	var c int;
	scan c;
	search(head,c);
};
