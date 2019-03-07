package main;
import "fmt";
import "math";

const s string = "constant";

func boo(){;};

type point struct {
    y,x int "hey";
};

    

type person struct {
    name string;
    age  int;
};


func main( ) {
    fmt.Println(s);
    foo();
    a := foo(b,c);
    var fgh int;
    const d int = 320 + 3 + 4 * 3 - a*5/3 ;
    const a,b,c = 1,2,"foo";
    fmt.Println(d);
    fmt.Println(x[5][3]);
    fmt.Println(math.Sin(n));
    fmt.Println("emp:", a);
    var a [5]int;
    
    for i = 0; i < 2; i++ {
        for j = 0; j < 3; j++ {
            if(a<0){
                twoD[i][j] = i + j;
            }else if(a==0){
                ;
            }else{boo();};  
        };
    };
    a[4] = 100;  
    var twoD [2][3]int;
    var ptr int ;   
    return 5.4+ 4;
    continue;
    break;
    x++;
    
    
};