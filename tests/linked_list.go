package main;

type rect struct {
    val  int;
    next *type rect;
};

func main(){
	var a [5]type rect;
	for i:=0;i<4;i++{
		a[i].next = &a[i+1];
		a[i].val = 10+i;
	};
	a[4].val = 14;
	a[4].next = null;
	print "Enter the No. to search: ";
	var k int;
	var flag int = 0;
	scan k;
	var b *type rect;
	b = &a[0];
	var j bool=true;
	for ;j;{
		print b.val;
		if k==b.val{
			flag=1;
			j=false;
		};
		print "\n";
		b = b.next;
		if b==null{
			j=false;
		};
	};
	if flag==1{
		print "Element Found\n";
	} else{
		print "Element Not found\n";
	};
};
