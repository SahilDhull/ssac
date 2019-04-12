// Factorial Case

package math;

func f(a int) int
{
	return a*f(a-1);
};

func main(){
	var a int = f(5);
};