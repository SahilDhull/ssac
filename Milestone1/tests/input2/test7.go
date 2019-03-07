package main;
import "fmt";



type rectangle struct {
    length  int;
    breadth int;
    color   string;
     
    geometry struct{
        area int;
        perimeter int;
    };
};
func main(){
    var x[5] int;    // Array Declaration
 
    x[0]=10;         // Assign the values to specific Index
    x[4]=20;         // Assign Value to array index in any Order 
    x[1]=30;
    x[3]=40;
    x[2]=50;
    fmt.Println("Values of Array X: ",x);
 
    // Array Declartion and Intialization to specific Index
    type y = [5] int;
    y[0] = 100;
    y[1] = 200;
    y[2] = 500;
    fmt.Println("Values of Array Y: ",y);
 

	
	
	
	type employee = map[string]int;
    employee["Mark"] = 10;
    employee["Sandy"] = 20;
    fmt.Println(employee);
    
    type employeeList = map[string]int;
    employeeList["Mark"] = 10;
    employeeList["Sandy"] = 20;
    fmt.Println(employeeList);
	
	
	
	var rect type rectangle;
    rect.length =  10;
    rect.breadth=  20;
    rect.color  =  "Green";
     
    rect.geometry.area   =  rect.length * rect.breadth;
    rect.geometry.perimeter =  2 * (rect.length + rect.breadth);
     
    fmt.Println(rect);
    fmt.Println("Area:\t", rect.geometry.area);
    fmt.Println("Perimeter:", rect.geometry.perimeter);
 
};