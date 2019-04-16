package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};

func main(){
	var a [5]type rect;
	for i:=0;i<4;i++{
		a[i].next = &a[i+1];
		a[i].age = 10+i;
	};
	a[4].age = 14;
	print "Enter the No. to search: ";
	var k int;
	var flag int = 0;
	scan k;
	var b *type rect;
	b = &a[0];
	for j:=0;j<5;j++{
		print b.age;
		if k==b.age{
			flag=1;
		};
		print "\n";
		b = b.next;
	};
	if flag==1{
		print "Element Found\n";
	} else{
		print "Element Not found\n";
	};
};
