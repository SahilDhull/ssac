package math;
import "fmt";

var a int;

func f(a int,b int) (int,int) {
	return a,b;
};

func g(a int,b int) int {
	return a;
};

func main() {
	var c,k int;
	f(c,k);
	g(c,k);
	// c = k-1;
};