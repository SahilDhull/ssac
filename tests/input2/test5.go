package main;
import (
	"fmt";
	"math";
);

type Abser int_t;

type Vertex struct {
	X, Y float_t;
};

 func Abs(v *type Vertex) float_t {
 	return math.Sqrt(v.X*v.Y+x.Y);
 };

 func main() {
 var a type Abser;
 f :=  typecast type MyFloat(a);
 var v type Vertex;
 v.X = 2;
	a = g.k+4;


 a = f;  // a MyFloat implements Abser
 a = &v; // a *Vertex implements Abser

 // In the following line, v is a Vertex (not *Vertex)
 // and does NOT implement Abser.
 a = v;
//fmt.Println(a.m);
 fmt.Println(Abs(a.n));
};

 type MyFloat float_t;

 func main (f type MyFloat) (float_t) {
 	if f < 0 {
 		return typecast float_t(-f);
 	};
 	return typecast float_t(-f);
 };


 
