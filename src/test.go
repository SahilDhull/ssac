package main;

func main(){
	var p *int;
	var a int = 5;
	p = &a;
	*p = 1;
	print *p;
};
