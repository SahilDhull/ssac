package main;

type node struct {
	a int;
	b *type node;
};

func main() {
	var x [10]*type node;
	var v,g *type node;
	for i := 0; i < 10; i++ {
		v = malloc(8);
		x[i] = v;
		for j := 0; j < 10; j++ {
			v.a = 10 + i*10 + j;
			g = malloc(8);
			v.b = g;
			v = v.b;
		};
	};

	for i := 0; i < 10; i++ {
		v = x[i];
		for j := 0; j < 10; j++ {
			print v.a,"\n";
			v = v.b;
		};
		print "--\n";
	};
};
