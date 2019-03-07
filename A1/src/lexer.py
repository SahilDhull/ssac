import ply.lex as lex
from random import shuffle
import sys
##Reserved Keywords in GoLang
keywords = {
	'break' : 'BREAK',
	'default' : 'DEFAULT',
	'func' : 'FUNC',
	'interface' : 'INTERFACE',
	'select' : 'SELECT',
	'case' : 'CASE',
	'defer' : 'DEFER',
	'go' : 'GO',
	'map' : 'MAP',
	'struct' : 'STRUCT',
	'chan' : 'CHAN',
	'else' : 'ELSE',
	'goto' : 'GOTO',
	'package' : 'PACKAGE',
	'switch' : 'SWITCH',
	'const' : 'CONST',
	'fallthrough' : 'FALLTHROUGH',
	'if' : 'IF',
	'range' : 'RANGE',
	'type' : 'TYPE',
	'continue' : 'CONTINUE',
	'for' : 'FOR',
	'import' : 'IMPORT',
	'return' : 'RETURN',
	'var' : 'VAR'
}

tokens = [
		#Literals
		'COMMENT','STRING','NEWLINE','IMAGINARY_LIT','FLOAT_LIT','INT_LIT','IDENTIFIERS','ERROR',

		#Operators
		'INCREMENT','DECREMENT','LEFT_ARROW', 'NOT', 'OR', 'AND', 'PLUSEQUAL','ANDEQUAL','COMPARE_AND',
		'EQUALS','NOTEQUALS', 'PLUS','MINUS','MINUSEQUAL','OREQUAL','COMPARE_OR','LESSTHAN',
		'LESSTHAN_EQUAL', 'MULTIPLY','XOR','TIMESEQUAL','XOREQUAL', 'GREATERTHAN', 'GREATERTHAN_EQUAL',
		'DIVIDE', 'LEFTSHIFT', 'DIVIDE_EQUAL', 'LEFTSHIFT_EQUAL','ASSIGNMENT','SHORT_ASSIGNMENT',
		'MODULO','RIGHTSHIFT','MODEQUAL','RIGHTSHIFT_EQUAL','ANDXOR','ANDXOR_EQUAL','DOTS',

		#PUNCTUATION
		'LEFT_PAREN','RIGHT_PAREN','LEFT_BRACKET','RIGHT_BRACKET','LEFT_BRACE','RIGHT_BRACE',
		'COMMA','PERIOD','SEMI_COLON','COLON','WHITESPACES'
] + list(keywords.values())

key = list(keywords.values())

punc = ['LEFT_PAREN','RIGHT_PAREN','LEFT_BRACKET','RIGHT_BRACKET','LEFT_BRACE','RIGHT_BRACE',
		'COMMA','PERIOD','SEMI_COLON','COLON','WHITESPACES']

op = ['INCREMENT','DECREMENT','LEFT_ARROW', 'NOT', 'OR', 'AND', 'PLUSEQUAL','ANDEQUAL','COMPARE_AND',
		'EQUALS','NOTEQUALS', 'PLUS','MINUS','MINUSEQUAL','OREQUAL','COMPARE_OR','LESSTHAN',
		'LESSTHAN_EQUAL', 'MULTIPLY','XOR','TIMESEQUAL','XOREQUAL', 'GREATERTHAN', 'GREATERTHAN_EQUAL',
		'DIVIDE', 'LEFTSHIFT', 'DIVIDE_EQUAL', 'LEFTSHIFT_EQUAL','ASSIGNMENT','SHORT_ASSIGNMENT',
		'MODULO','RIGHTSHIFT','MODEQUAL','RIGHTSHIFT_EQUAL','ANDXOR','ANDXOR_EQUAL','DOTS']

integer = ['IMAGINARY_LIT','FLOAT_LIT','INT_LIT']

#operators
t_INCREMENT                = r'\+\+'
t_DECREMENT                = r'--'
t_LEFT_ARROW               = r'<-'
t_NOT                      = r'!'
t_OR                       = r'\|'
t_AND                      = r'&'
t_PLUSEQUAL                = r'\+=' 
t_ANDEQUAL 				   = r'&='
t_COMPARE_AND              = r'&&'
t_EQUALS                   = r'=='
t_NOTEQUALS                = r'!='
t_PLUS                     = r'\+'
t_MINUS                    = r'-'
t_MINUSEQUAL               = r'-='
t_OREQUAL                  = r'\|='
t_COMPARE_OR               = r'\|\|'
t_LESSTHAN                 = r'<'
t_LESSTHAN_EQUAL           = r'<='
t_MULTIPLY                 = r'\*'
t_XOR                      = r'\^'
t_TIMESEQUAL               = r'\*='
t_XOREQUAL                 = r'\^='
t_GREATERTHAN              = r'>'
t_GREATERTHAN_EQUAL        = r'>='
t_DIVIDE                   = r'/'
t_LEFTSHIFT                = r'<<'
t_DIVIDE_EQUAL             = r'/='
t_LEFTSHIFT_EQUAL          = r'<<='
t_ASSIGNMENT               = r'='
t_SHORT_ASSIGNMENT         = r':='
t_MODULO                   = r'%'
t_RIGHTSHIFT               = r'>>'
t_MODEQUAL                 = r'%='
t_RIGHTSHIFT_EQUAL         = r'>>='
t_ANDXOR                   = r'&\^'
t_ANDXOR_EQUAL             = r'&\^='
t_DOTS                     = r'\.\.\.'


#Punctuation
t_LEFT_PAREN               = r'\('
t_RIGHT_PAREN              = r'\)'
t_LEFT_BRACKET             = r'\['
t_RIGHT_BRACKET            = r'\]'
t_LEFT_BRACE               = r'\{'
t_RIGHT_BRACE              = r'\}'
t_COMMA                    = r','
t_PERIOD                   = r'\.'
t_SEMI_COLON               = r';'
t_COLON                    = r':'
t_WHITESPACES              = r'(\t)|(\s)'

#Literals
# t_IDENTIFIERS              = r'[A_Za-z_][A-Za-z0-9_]*'
# t_NEWLINE                  = r'\n'
# t_LETTER                   = r'[A-Za-z_]'
# t_INT_LIT                  = r'(0[xX][0-9a-fA-F][0-9a-fA-F]*)|(0[0-7]*)|([1-9][0-9]*)'
# t_FLOAT_LIT                = r'([0-9][0-9]*\.[0-9]+?([eE][\+-]?[0-9][0-9]*)?)|([0-9]+[eE][\+-]?[0-9][0-9]*)|(\.[0-9]+([eE][\+-]?[0-9][0-9]*)?)'
#t_EXPONENT                 = r'[eE][\+-]?[0-9][0-9]*'
# t_IMAGINARY_LIT            = r'([0-9]+|([0-9][0-9]*\.[0-9]+?([eE][\+-]?[0-9][0-9]*)?)|([0-9]+[eE][\+-]?[0-9][0-9]*)|(\.[0-9]+([eE][\+-]?[0-9][0-9]*)?)[i])'
# t_STRING                   = r'(\'([\^\n]|[\n])*\')|("[\^\n]*")'
def t_COMMENT(t):
	r'(/\*(.|\n)*?\*/)|(//.*)'
	t.lexer.lineno += t.value.count('\n')
	return t

def t_STRING(t):
	# r'(\'([\^\n]|[\n])*\')|(\"([^\\\n]|(\\.))*?\")'
	r'((L)?\'([^\\\n]|(\\.))*?\')|(\"([^\\\n]|(\\.))*?\")'
	return t

def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	return t

def t_IMAGINARY_LIT(t):
	r'(([0-9]+)|(([0-9]+\.([0-9]+)?([eE][\+-]?[0-9]+)?)|([0-9]+[eE][\+-]?[0-9]+)|(\.[0-9]+([eE][\+-]?[0-9]+)?)))[i]'
	return t

def t_FLOAT_LIT(t):
	r'([0-9]+\.([0-9]+)?([eE][\+-]?[0-9]+)?)|([0-9]+[eE][\+-]?[0-9]+)|(\.[0-9]+([eE][\+-]?[0-9]+)?)'
	return t

# flo = r'([0-9]+\.([0-9]+)?([eE][\+-]?[0-9]+)?)|([0-9]+[eE][\+-]?[0-9]+)|(\.[0-9]+([eE][\+-]?[0-9]+)?)')
#dec = r'[0-9]+'
#exp = r'[eE][\+-]?[0-9]+'
def t_INT_LIT(t):
	r'(0[xX][0-9a-fA-F][0-9a-fA-F]*)|(0[0-7]*)|([1-9][0-9]*)'
	return t

def t_IDENTIFIERS(t):
	r'[A-Za-z_][A-Za-z0-9_]*'
	t.type = keywords.get(t.value,'IDENTIFIERS')
	return t

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# colors = ['1C0122', '043904', '530B22', '000000', '196286', '7D541F', '1C0D54']
# shuffle(colors)
# # for x in range(len(tokens)):
# # 	print(tokens[x],",",uuid.uuid4().hex.upper()[0:6])
# # # print(uuid.uuid4().hex.upper()[0:6])

# print("NEWLINE,000000")
# print("ERROR,000000")
# print("IDENTIFIERS,",colors[4])
# print("STRING,",colors[5])
# print("COMMENT,",colors[6])

# for x in range(len(key)):
# 	print(key[x],",",colors[0])

# for x in range(len(punc)):
# 	print(punc[x],",",colors[1])

# for x in range(len(op)):
# 	print(op[x],",",colors[2])

# for x in range(len(integer)):
# 	print(integer[x],",",colors[3])
# sys.exit()

#  Build the lexer
lexer = lex.lex()
check1 = sys.argv[1][:6]
# print(check1)
if check1!='--cfg=':
	print ("wrong command")
	print("Type 2nd argument as '--cfg=...'")
	sys.exit()
colorfile = sys.argv[1][6:]
inputfile = sys.argv[2]
check2 = sys.argv[3][:9]
# print(check2)
if check2!='--output=':
	print ("wrong command")
	print("Type last argument as '--output=...'")
	sys.exit()
outputfile = sys.argv[3][9:]
check3 = sys.argv[3][-5:]
# print(check3)
# sys.exit()
if check3!='.html':
	print ("wrong command")
	print("Save output as html file")
	sys.exit()
d = {}
file =  open(colorfile,'r')
for line in file:
	x =line.split(",")
	a = x[0]
	b = x[1]
	d[a] = b
inputfile_1 = open(inputfile,'r')
data = inputfile_1.read()
lexer.input(data)	
with open(outputfile,'w') as e:
	e.write('<html><body><div><pre>\n')
	while True:
		tok = lexer.token()
		if not tok:
			break
		print (tok)
		e.write('<span style ="color:%s;">'% d[tok.type] +tok.value+'</span>')
	e.write("</body></html>")