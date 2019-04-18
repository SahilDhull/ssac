package main;

type node struct {
	val int;
	next *type node;
};

func main() {
	// Array of struct
	var a [5]type node;
	for i:=0;i<4;i++{
		a[i].next = &a[i+1];
		a[i].val = i;
	};
	a[4].next = null;
	a[4].val = 4;
	print a[1].next.next.next.val,"\n";
	// Array of strings
	var s [6]string;
	for i:=0;i<6;i++{
		switch i {
		case 0:
			s[i]="Shubham\n";
		case 1:
			s[i]="Sahil\n";
		case 2:
			s[i]="Ankit\n";
		case 3:
			s[i]="Compiler\n";
		case 4:
			s[i]="Combine to form : ";
		default:
			s[i]="ssac\n";
		};
	};
	for i:=0;i<6;i++{
		print s[i];
	};
};