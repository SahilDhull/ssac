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
	}else if c<head.val{
		search(head.l,c);
	}
	else if c>head.val{
		search(head.r,c);
	}
	else{
		print c," : Key found\n";
	};
	return;
};

func insert(head *type node, c int) *type node{
	if head == null{
		head = malloc(12);
		head.val=c;
		head.l = null;
		head.r = null;
	}
	else if c<head.val{
		head.l = insert(head.l,c);
	}
	else if c>head.val{
		head.r = insert(head.r,c);
	}
	else{
		print c," : This Key already exists\n";
	};
	return head;
};

func main() {
	var head *type node;
	head = null;
	head = insert(head,3);
	head = insert(head,1);
	head = insert(head,5);
	print "Inorder of BST:\n";
	bst(head);
	print "\nEnter Element to find: ";
	var c int;
	scan c;
	search(head,c);
};
