package main;


func main() {
	var n int;
	n = 5;
	var a [5]int;
	var c int;
	var i int;
	var start int;
	var end int;
	var key int;
	var m int;
	var flag int;
	flag = 0;
	print "Enter 5 elements : \n";
	for i = 0; i < n; i++ {
		scan c;
		a[i] = c;
	};
	for i = 0; i < n; i++ {
		print a[i]," ";
	};

	start = 0;
	end = n - 1;
	// key = 8;
	print "\nEnter key to be searched\n";
	scan key;
	for ;start <= end; {
		m = start + (end-start)/2;
		if a[m] == key {
			flag =1 ;
			print "found at index ";
			print m;
		};

		if a[m] < key {
			start = m + 1;
		} else {
			end = m - 1;
		};
	};
	if flag == 0{
		print "key not found";
	};
	print "\n";
};
