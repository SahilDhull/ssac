package main;

func main(){
	var c int;
	scan c;
	var k int;
	switch c {
	case 0,1:
		k=2;
	case 2:
		k=3;
	default:
		k=5;
	};
	print k;
};

