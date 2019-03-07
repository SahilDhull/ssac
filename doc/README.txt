Source Language is GO
Implementation language is Python


Command to build and run: (considering you are in the directory cs335_160120)
cd src
make
./AST ../tests/input2/test<x>.go --out=test<x>.dot

where x can be from 1 to 10


The following command will generate the ps file for the AST:
dot -Tps test<x>.dot -o t<x>.ps


The directory structure is:
1. doc			- README.txt and PDF
2. src			- lexer.py
3. tests		- 2 directories - cfg1 and input1
4. tests/input1		- 5 input files in .go format for testing lexer
5. tests/input2		- 10 input files in .go format for testing parser

any discrepancy with input format leads to error displaying.


For printing Tokens, Lexemes and their occurrences:
Uncomment the last lines of lexer.py, they will be displayed in terminal.
Also, lexer.py has been changed to give tokens to parser rather than generating html file as in assignment 1.
