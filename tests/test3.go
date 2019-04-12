// pointer

package math;

import "fmt";

func main(){
	var a,b int = 1,2;
	var p *int;
	p = &a;
	*p = 3;
};