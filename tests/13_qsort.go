package main;

func partition(p int, r int, A [10]int) (int, [10]int) {
	print "Partition ";
	print p;
	print " ";
	print r;
	print "\n";
	x := A[p];
	i := p - 1;
	j := r + 1;

	for ;;{
		j--;
		kk := A[j];
		for kk < x {
			// fmt.Printf("J loop yes %d %d\n", A[j], x)
			j--;
			kk = A[j];
		};
		i++;
		for A[i] > x {
			// fmt.Printf("I loop yes %d %d\n", A[i], x)
			i++;
		};
		if i < j {
			tmp := A[i];
			A[i] = A[j];
			A[j] = tmp;
		}; 
		else {
			// fmt.Printf("Returning value: %d\n", j)
			return j,A;
		};
	};
	// fmt.Printf("Never reach here")
	return -1,A;
};


func qsort(p int, r int, A [10]int) ([10]int){
	if p < r {
		q, A := partition(p, r, A);
		print "Value returned: ";
		print q;
		print "\n";
		A = qsort(p, q, A);
		A = qsort(q+1, r, A);
		return A;
	};
};

func main() {
	var A [10]int;

	for i := 0; i < 10; i++ {
		n := 0;
		scan n;
		A[i] = n;
	};

	A = qsort(0,9,A);

	for i := 0; i < 10; i++ {
		print A[i];
		print "$$$";
	};

};
