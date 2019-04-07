package math;
import "fmt";

var a int;

type rect struct {
    name string;
    age  int;
    next *type rect;
};

func main() {
	var x *type rect = malloc(2);
	var l *int = malloc(1);
};