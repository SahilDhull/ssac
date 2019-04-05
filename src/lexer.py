#!/usr/bin/env python2
import ply.lex as lex
from random import shuffle
import sys
##Reserved Keywords in GoLang
keywords = {
	'break' : 'BREAK',
	'default' : 'DEFAULT',
	'func' : 'FUNC',
	'case' : 'CASE',
	'defer' : 'DEFER',
	'go' : 'GO',
	'map' : 'MAP',
	'struct' : 'STRUCT',
	'else' : 'ELSE',
	'goto' : 'GOTO',
	'package' : 'PACKAGE',
	'switch' : 'SWITCH',
	'const' : 'CONST',
	'fallthrough' : 'FALLTHROUGH',
	'if' : 'IF',
	'type' : 'TYPE',
	'continue' : 'CONTINUE',
	'for' : 'FOR',
	'import' : 'IMPORT',
	'return' : 'RETURN',
	'var' : 'VAR',
	'typecast' : 'TYPECAST',
	'int' : 'INT',
	'float' : 'FLOAT',
	'string' : 'STRING',
	'bool' : 'BOOL',
	'print' : 'PRINT',
	'scan' : 'SCAN',
	'malloc' : 'MALLOC'
}

tokens = [
		#Literals
		'STRING_LIT','IMAGINARY_LIT','FLOAT_LIT','INT_LIT','IDENTIFIER',
		# 'NEWLINE',
		#Operators
		'INCREMENT','DECREMENT', 'NOT', 'OR', 'AND', 'PLUSEQUAL','ANDEQUAL','COMPARE_AND',
		'EQEQ','NOTEQUALS', 'PLUS','MINUS','MINUSEQUAL','OREQUAL','COMPARE_OR','LESSTHAN',
		'LESSTHAN_EQUAL', 'MULTIPLY','XOR','TIMESEQUAL','XOREQUAL', 'GREATERTHAN', 'GREATERTHAN_EQUAL',
		'DIVIDE', 'LSHIFT', 'DIVIDE_EQUAL', 'LSHIFT_EQUAL','EQUALS','SHORT_ASSIGNMENT',
		'MODULO','RSHIFT','MODEQUAL','RSHIFT_EQUAL','ANDXOR','ANDXOR_EQUAL',

		#PUNCTUATION
		'LPAREN','RPAREN','LSQUARE','RSQUARE','LCURL','RCURL',
		'COMMA','DOT','SEMICOLON','COLON',
		'PD','PS'
] + list(keywords.values())

t_PD = r'%d'
t_PS = r'%s'

#operators
t_INCREMENT                = r'\+\+'
t_DECREMENT                = r'--'
t_NOT                      = r'!'
t_OR                       = r'\|'
t_AND                      = r'&'
t_PLUSEQUAL                = r'\+=' 
t_ANDEQUAL 				   = r'&='
t_COMPARE_AND              = r'&&'
t_EQEQ                  = r'=='
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
t_LSHIFT                = r'<<'
t_DIVIDE_EQUAL             = r'/='
t_LSHIFT_EQUAL          = r'<<='
t_EQUALS               = r'='
t_SHORT_ASSIGNMENT         = r':='
t_MODULO                   = r'%'
t_RSHIFT               = r'>>'
t_MODEQUAL                 = r'%='
t_RSHIFT_EQUAL         = r'>>='
t_ANDXOR                   = r'&\^'
t_ANDXOR_EQUAL             = r'&\^='
# t_DOTS                     = r'\.\.\.'


#Punctuation
t_LPAREN               = r'\('
t_RPAREN              = r'\)'
t_LSQUARE             = r'\['
t_RSQUARE            = r'\]'
t_LCURL               = r'\{'
t_RCURL              = r'\}'
t_COMMA                    = r','
t_DOT                   = r'\.'
t_SEMICOLON               = r';'
t_COLON                    = r':'
t_ignore_WHITESPACES              = r'(\t)|(\s)'

#Literals
# t_IDENTIFIERS              = r'[A_Za-z_][A-Za-z0-9_]*'
# t_NEWLINE                  = r'\n'
# t_LETTER                   = r'[A-Za-z_]'
# t_INT_LIT                  = r'(0[xX][0-9a-fA-F][0-9a-fA-F]*)|(0[0-7]*)|([1-9][0-9]*)'
# t_FLOAT_LIT                = r'([0-9][0-9]*\.[0-9]+?([eE][\+-]?[0-9][0-9]*)?)|([0-9]+[eE][\+-]?[0-9][0-9]*)|(\.[0-9]+([eE][\+-]?[0-9][0-9]*)?)'
#t_EXPONENT                 = r'[eE][\+-]?[0-9][0-9]*'
# t_IMAGINARY_LIT            = r'([0-9]+|([0-9][0-9]*\.[0-9]+?([eE][\+-]?[0-9][0-9]*)?)|([0-9]+[eE][\+-]?[0-9][0-9]*)|(\.[0-9]+([eE][\+-]?[0-9][0-9]*)?)[i])'
# t_STRING                   = r'(\'([\^\n]|[\n])*\')|("[\^\n]*")'

t_ignore_COMMENT = r'(/\*([^*]|\n|(\*+([^*/]|\n])))*\*+/)|(//.*)'

# def t_ignore_COMMENT(t):
# 	r'(/\*(.|\n)*?\*/)|(//.*)'
# 	t.lexer.lineno += t.value.count('\n')
# 	return t

def t_STRING_LIT(t):
	# r'(\'([\^\n]|[\n])*\')|(\"([^\\\n]|(\\.))*?\")'
	r'((L)?\'([^\\\n]|(\\.))*?\')|(\"([^\\\n]|(\\.))*?\")'
	return t

def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	# return t

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

def t_IDENTIFIER(t):
	r'[A-Za-z_][A-Za-z0-9_]*'
	t.type = keywords.get(t.value,'IDENTIFIER')
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


Toks={}
for a in tokens:
    Toks[a]=[a,0]

file_name = sys.argv[1]	

# ------ output check ----------------
# check2 = sys.argv[2][:6]
# # print(check2)
# if check2!='--out=':
# 	print ("wrong command")
# 	print("Type last argument as '--out=...'")
# 	sys.exit()
# out_name = sys.argv[2][6:]

with open(file_name) as fp:
    data = fp.read()
    data += '\n'
    lexer.input(data)

    
    while True:
        tok = lexer.token()
        if not tok:
            break
        # print (tok)
        Toks[tok.type][1]=Toks[tok.type][1]+1
        if tok.value in Toks[tok.type][2:]:
            continue
        Toks[tok.type].append(tok.value)

    # print "TOKEN\t\t\tOCCURRENCES\t\tLEXEMES"
    # print "-"*64
    # for i in Toks:
    #     if Toks[i][1]==0:
    #         continue
    #     if len(Toks[i][0]) <= 6:
    #         print Toks[i][0], "\t\t\t", Toks[i][1], "\t\t\t", Toks[i][2]
    #     else:
    #         print Toks[i][0], "\t\t", Toks[i][1], "\t\t\t", Toks[i][2]
    #     for x in range(3, len(Toks[i])):
    #         print "\t\t\t\t\t\t", Toks[i][x]