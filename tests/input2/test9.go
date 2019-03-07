
package main;

import "fmt";

type person struct {
    name string;
    age  int;
};
func vals() (int, int) {
    return  3,7;
};


func zeroval(ival int) {
    ival = 0;
};

func zeroptr(iptr *int) {
    *iptr = 0;
};


func main() {

    var s type person;
    s.name = "non";
    s,age=20;
    fmt.Println(s);

    
    sp := &s;
    fmt.Println(sp.age);


    sp.age = 51;
    fmt.Println(sp.age);

        

    i := 1;
    fmt.Println("initial:", i);
    zeroval(i);
    fmt.Println("zeroval:", i);

    zeroptr(&i);
    fmt.Println("zeroptr:", i);

    fmt.Println("pointer:", &i);
};
