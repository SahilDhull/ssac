package main;
 
import (
	"fmt";
	"time";
);
 
func main() {
	//today := time.Now();
 
	switch 5 {
	case 5:
		fmt.Println("Today is 5th. Clean your house.");
	case 10:
		fmt.Println("Today is 10th. Buy some wine.");
	case 15:
		fmt.Println("Today is 15th. Visit a doctor.");
	case 25:
		fmt.Println("Today is 25th. Buy some food.");
	case 31:
		fmt.Println("Party tonight.");
	default:
		fmt.Println("No information available for that day.");
	};
	k := 1;
	for ; k <= 10; k++ {
		fmt.Println(k);
	};
 
	k = 1;
	for k <= 10 {
		fmt.Println(k);
		k++;
	};
 
	for k := 1; ; k++ {
		fmt.Println(k);
		if k == 10 {
			break;
		};
	};
	x := 100;
 
	if x == 100 {
		fmt.Println("Japan");
	}
	else {
		fmt.Println("Canada");
	};
};
