package main;
import "fmt";
func even(number int) int;
func odd(number int) int;
func odd(number int) int {
	if (number==0) {
		return 0;
	}
	else{
		return even(number-1);
	};
};

func even(number int) int {
	if(number==0) {
		return 1;
	}
	else{
		return odd(number-1);
	};
};
func main ()

{
	// set an integer number here
	var number int = 23945;
	// if the number is odd (1 = TRUE)
	if odd(number)==1{
		print "number is odd";
	}
	else {
		print "number is even";
	};
	return 0;
};
 
// returns 0 if the given number becomes 0, so the given number is odd
// returns even(number - 1) elsewhere

 
// returns 0 if the given number becomes 0, so the given number is even
// returns odd(number - 1) elsewhere
