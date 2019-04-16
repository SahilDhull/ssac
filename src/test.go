package main;

type rect struct {
    name string;
    age  int;
    next *type rect;
};


func main(){

	// var a [4]type rect;
	// a[0].name = "shubham\n";
	// a[0].age = 21;
	// a[1].name = "sahil\n";
	// a[1].age = 23;
	// a[2].name = "ankit\n";
	// a[2].age = 19;
	// a[3].name = "kushlam\n";
	// a[3].age = 30;

	// for j:=0;j<3;j++{
	// 	a[j].next = &a[j+1];
	// };	

	// var b *type rect;
	// b = &a[0];
	// for i:=0;i<4;i++{
	// 	print b.name,b.age,"\n---------\n";
	// 	b = b.next;
	// };

	var a1 [2]string;
	a1[0] = "hellooooooo";
	a1[1] = "worlddddddd";
	a1[1] = a1[0];
	print a1[0],"\n",a1[1],"\n";

	// var a,b string;
	// a = "hello\n";
	// b = "world\n";
	// a = b;
	// print a,b;



	// var a2 [3]int;
	// a2[0] = 1;
	// a2[1] = 2;
	// a2[2] = 3;
	// a2[2] = 1;

	// print a2[0],"\n",a2[1],"\n",a2[2],"\n";

};
