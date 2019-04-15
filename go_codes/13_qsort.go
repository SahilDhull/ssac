package main;

<<<<<<< HEAD
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
=======
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
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
	};
};

func main() {
<<<<<<< HEAD
	var A [4]int;
	var i,n,j int;
	for i = 0; i < 4; i++ {
		// n = 0;
		// print i;
		// print "\n";
=======
	var A [10]int;

	for i := 0; i < 10; i++ {
		n := 0;
>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
		scan n;
		A[i] = n;
	};

<<<<<<< HEAD
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
=======
	A = qsort(0,9,A);

	for i := 0; i < 10; i++ {
		print A[i];
		print "$$$";
	};

>>>>>>> de83aab19d78354e4f22a0c67b062115ea828b33
};
