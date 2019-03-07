
package main;

import (
	"fmt";
);

func main() {
	var res, i, j, k int;
	for res, i = 0, 0; i < 10; i++ {
		for j = 0; j < 10; j++ {
			for k = 0; k < 10; k++ {
				res += 1;
			};
		};
	};
	fmt.Printf("res = %d\n", res);
	const x =1;
};