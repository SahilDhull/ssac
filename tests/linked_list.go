package main;

type node struct {
    val  int;
    next *type node;
};

func insert(head *type node, c int) *type node{
	if head == null{
		head = malloc(8);
		head.val = c;
		head.next = null;
	} else{
		head.next = insert(head.next,c);
	};
	return head;
};

func print_linked_list(head *type node){
	if head == null{
		return;
	}
	else{
		print head.val," ";
		print_linked_list(head.next);
	};
	return;
};

func search(head *type node,c int){
	if head == null{
		print c," : Not Found\n";
		return;
	}
	else if head.val==c{
		print c," : Found\n";
		return;
	}
	else{
		search(head.next,c);
	};
	return;
};

func main(){
	var head *type node;
	head = null;
	var n,c int;
	print "No. of nodes in Linked List : ";
	scan n;
	for i:=0;i<n;i++{
		scan c;
		head = insert(head,c);
	};
	print "Linked List is as follows: ";
	print_linked_list(head);
	print "\nEnter the No. to search: ";
	scan c;
	search(head,c);
};
