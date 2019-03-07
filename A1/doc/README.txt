Source Language is GO
Implementation language is Python (Python3)


Command to build and run: (considering you are in the directory cs335_160120)
python3 src/lexer.py --cfg=tests/cfg1/color{x}.txt tests/input1/input{y}.go --output=some.html

where x can be from 1 to 3 and y can be from 1 to 5


The directory structure is:
1. doc			- README.txt and PDF
2. src			- lexer.py
3. tests		- 2 directories - cfg1 and input1
4. tests/input1		- 5 input files in .go format
5. tests/cfg1		- 3 configuration files

any discrepancy with input format leads to error displaying.
