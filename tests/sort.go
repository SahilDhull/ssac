package main;

func main() {
	var b [5]int;
	b[0] = 7;
	b[1] = 5;
	b[2] = 9;
	b[3] = 2;
	b[4] = 6;
	for i := 0; i < 5; i++ {
		for j := 0; j < 4; j++ {
			if b[j] > b[j+1] {
				c := b[j];
				b[j] = b[j+1];
				b[j+1] = c;
			};
		};
	};

	for i := 0; i < 5; i = i + 1 {
		print b[i];
		print "\n";
	};
};
