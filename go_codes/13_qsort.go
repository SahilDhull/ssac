package main;

import "fmt";

func partition(A [4] int,p int, r int) int {
	// fmt.Printf("Partition %d %d\n", p, r);
	var x,i,j,kk int;
	var tmp int;
	x = A[r];
	i = p - 1;
	for j=p; j<=r-1 ;j++{
		if A[j] <= x {
			i++;
			tmp = A[j];
			A[j] = A[i];
			A[i] = tmp;
		};
	};
	tmp = A[j];
	A[j] = A[i];
	A[i] = tmp;
	// print "Never reach here";
	return i+1;
};
func qsort(A [4] int,p int, r int)  {
	var q int; 
	if p < r {
		// print "here";
		q = partition(A,p,r);
		// print q;
		// fmt.Printf("Value returned: %d\n", q);
		qsort(A,p, q-1);
		qsort(A,q+1, r);
	};
};

func main() {
	var A [4]int;
	var i,n,j int;
	for i = 0; i < 4; i++ {
		// n = 0;
		// print i;
		// print "\n";
		scan n;
		A[i] = n;
	};

	for i = 0; i < 4; i++ {
		print A[i];
		print " ";
	};
	// print "\n";
	// print "here";
	print "\n";
	qsort(A,0,3);

	for i = 0; i < 4; i++ {
		print A[i];
		print " ";
	};
	print "\n";
};
