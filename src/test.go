package main;

func main(){
	var k string;
	var p *string;
	p = &k;
	*p = "ok";
	// *p = 3;
	// print *p;
	// print "\n";
};