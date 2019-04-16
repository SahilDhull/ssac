package main;

func partition(p int, r int, A [10]int) (int, [10]int) {
	var x,i int;
	x = A[r];
	i = p - 1;
	// j := r + 1;
	var j int;
	var tmp int;
	for j = p;j <= r-1;j++{
		if (A[j] <= x){
			i++;
			tmp  = A[j];
			A[j] = A[i];
			A[i] = tmp;
		};
	};
	tmp  = A[j];
	A[j] = A[i+1];
	A[i+1] = tmp;
	// print A[i+1];
	// fmt.Printf("Never reach here")
	return i+1,A;
};


func qsort(p int, r int, A [10]int) ([10]int){
	var q int;
	if p < r {
		q, A = partition(p, r, A);
		// print "Value returned: ";
		// print q;
		// scan q;
		// print "\n";
		A = qsort(p, q-1, A);
		// scan q;
		A = qsort(q+1, r, A);
		
	};
	return A;
};

func main() {
	var A [10]int;
	// var B [10]int;
	var c,b,a int;
	for i := 0; i < 10; i++ {
		n := 0;
		// scan n;
		A[i] = 10*i - i;
	};

	A = qsort(0,9,A);
	for i := 0; i < 10; i++ {
		print A[i];
		print " ";
	};
	print "\n";

};
