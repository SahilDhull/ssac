
package main;


func main() {
	var a [4][4] int;
	var b [4][4] int;
	var res [4][4] int;

	var c int;
	var i int;
	var j int;
	var d int;
	var e int;
	var k int;
	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			scan c
			a[i][j] = i;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			scan c
			b[i][j] = i;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			c = 0;
			for k = 0; k < 4; k++ {
				d = a[i][k];
				e = b[k][j];
				c += d * e;
			};
			res[i][j] = c;
		};
	};

	for i = 0; i < 4; i++ {
		for j = 0; j < 4; j++ {
			print res[i][j];
			print " ";
		};
		print "\n";
	};
};

