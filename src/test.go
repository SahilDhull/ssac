package main;

func f(b [2][3]int) (int,[2][3]int) {
	var c int = b[1][2];
	return c,b;
};

func main(){
	var a [2][3]int;
	f(a);
};
