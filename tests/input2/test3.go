package main;

import (
	"fmt";
	"math/cmplx";
);

var (
	ToBe   bool_t      = false;
	MaxInt int_t     = 1<<64 - 1;
	z      complex_t = cmplx.Sqrt(-5 + 12i);
);

func fa(a int_t,b int_t){
	;
};

func main() {
	fa(ToBe, ToBe);
	fa(MaxInt, MaxInt);
	fa(z, z);
	fmt.Println("Hello");
};
