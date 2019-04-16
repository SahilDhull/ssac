package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};

func main(){
	var a *int;
	var b int;
	a = &b;
	var t *type rect;
	t = null;
	// print t;
	// print a;
	if a!=null && t==null{
		print "Coooool\n";
	};
	var j bool =true;
	for ;j;{
		j=false;
	};
};