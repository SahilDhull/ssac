package main;


var a int;
func f(a int,b int) (int,int){
	return a,4;
};

func main() {
	var b int = 1;
	var c,d int = f(2,1);
	print %d d;
};