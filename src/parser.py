#!/usr/bin/env python2
import ply.yacc as yacc
import sys
import os
from lexer import *
from symbol import *
# from scope import *

root = None

def size_calculate(s):
	if s=='int' or s=='cint' or s=='float' or s=='cfloat' or s=='bool' or s=='cbool' :
		return 4
	if s=='string' or s == 'cstring':
		return 32
	return 0


# -------------  PRINT FUNCTIONS ----------------

# def printnode():

def print_list(l):
	for i in l:
		print i

def print_scope_Dict():
	for i in range(len(scopeDict)):
		print "scopeDict["+str(i)+"] :"
		print scopeDict[i].__dict__
		print ""


# ----------  TYPE CHECKING -------------------

def equalcheck(x,y):
	if type(x) is list:
		x=x[0]
	if type(y) is list:
		y=y[0]
	if x==y:
		return True
	elif y.startswith('c') and x==y[1:]:
		return True
	elif x.startswith('*') and y=='*NULL':
		return True
	return False

def checkid(name,str,flag=0):
	if str=='andsand':
		if scopeDict[curScope].retrieve(name) is not None:
			info = scopeDict[curScope].retrieve(name)
			if info.type!=('type'+name):
				return True
		return False
	if str=='label':
		if scopeDict[0].retrieve(name) is not None:
			return True
		return False
	if str=='e':
		
		if scopeDict[curScope].retrieve(name) is not None:
			return True
		if flag==1:
			for scope in scopeStack[::-1]:
				if scopeDict[scope].retrieve(name) is not None:
					return True
		return False

	return False

def checkinparent(name,scope):
	if scopeDict[scope].retrieve(name) is not None:
		return True
	return False

def opTypeCheck(a,b,op):
	if type(a) is list:
		a = a[0]
	if type(b) is list:
		b = b[0]
	if a.startswith('*') and b.startswith('*'):
		return False
	if a.startswith('c') and a[1:]==b:
		return True
	if b.startswith('c') and a==b[1:]:
		return True
	if a==b:
		return True
	if a.startswith('c') and b.startswith('c') and a[1:]==b[1:]:
		return True
	if op=='+' or op=='-':
		if a.startswith('*') and (b=='int' or b=='cint'):
			return True
		if b.startswith('*') and (a=='int' or a=='cint'):
			return True
	return False


# ------------   SCOPE    ----------------------

curScope = 0
scopeLevel = 0
varNum = 0
cvarNum = 0
arrNum = 0
labelNum = 1
constNum = 0
mainFunc = True

cname = {}
labelDict = {}
scopeDict = {}
scopeDict[0] = st(0)
scopeDict[0].updateExtra('curOffset',0)
scopeStack=[0]

def addscope(name=None,off = 0):
	
	global scopeLevel
	global curScope
	scopeLevel+=1
	scopeStack.append(scopeLevel)
	scopeDict[scopeLevel] = st(scopeLevel)
	scopeDict[scopeLevel].setParent(curScope)
	scopeDict[scopeLevel].updateExtra('curOffset',off)
	# if mainFunc:
	#   y = scopeDict[0].extra['curOffset']
	#   scopeDict[scopeLevel].updateExtra('curOffset',y)
	if name is not None:
		# Not sure if correct
		
		if type(name) is list:
			# Fuction scope addition
			scopeDict[curScope].insert(name[1],'func')
			scopeDict[curScope].insert(name[1],'child',scopeDict[scopeLevel])
		else:
			# Struct scope addition
			if checkid(name,'e'):
				raise NameError(name+" already defined")
			scopeDict[curScope].insert(name, 'type'+name)
			scopeDict[curScope].updateAttr(name, 'child',scopeDict[scopeLevel])
	curScope = scopeLevel

def endscope():
	global curScope
	curScope = scopeStack.pop()
	curScope = scopeStack[-1]

def findscope(name):
	for s in scopeStack[::-1]:
		if scopeDict[s].retrieve(name) is not None:
			return s
	raise NameError(name+ " is not defined in any scope")

def findinfo(name, S=-1):
	if S > -1:
		if scopeDict[S].retrieve(name) is not None:
			return scopeDict[S].retrieve(name)
		raise NameError("Identifier " + name + " is not defined!")
	for scope in scopeStack[::-1]:
		if scopeDict[scope].retrieve(name) is not None:
			info = scopeDict[scope].retrieve(name)
			return info
	raise NameError("Identifier " + name + " is not defined!")


# -------------  SOME OTHER FUNCTIONS ---------------------

def v_decl(v,s,size=4):
	scopeDict[s].insert(v,None)
	vinfo = findinfo(v)
	scopeDict[s].extra['curOffset'] -= size
	vinfo.offset = scopeDict[s].extra['curOffset']
	vinfo.mysize = size

def newcvar():
	global cvarNum
	val = 'cv'+str(cvarNum)
	cvarNum += 1
	return val

def newvar():
	global varNum
	val = 'var'+str(varNum)
	# scopeDict[curScope].insert(val,None)
	varNum+=1
	return val

def newconst(typ='int'):
	global constNum
	val = 'temp_c'+str(constNum)
	scopeDict[curScope].insert(val,None)
	info = findinfo(val,curScope)
	scopeDict[curScope].extra['curOffset'] -= 4
	info.offset = scopeDict[curScope].extra['curOffset']
	info.mysize = 4
	info.type = typ
	constNum+=1
	return val

def newlabel():
	global labelNum
	val = 'l'+str(labelNum)
	labelNum+=1
	return val

def newarray():
	global arrNum
	val = 'arr_'+str(arrNum)
	scopeDict[curScope].insert(val,None)
	info = findinfo(val,curScope)
	scopeDict[curScope].extra['curOffset'] -= 4
	info.offset = scopeDict[curScope].extra['curOffset']
	info.mysize = 4
	arrNum += 1
	return val

#   ----------------------------------------------------


precedence = (
		('left', 'IDENTIFIER'),
		('right','EQUALS', 'NOT'),
		('left','INT_LIT'),
		('left','FLOAT_LIT'),
		('left','STRING_LIT'),
		('left', 'COMPARE_OR'),
		('left', 'COMPARE_AND'),
		('left', 'EQEQ', 'NOTEQUALS'),
		('left', 'OR'),
		('left', 'XOR'),
		('left', 'AND', 'ANDXOR'),
		('left', 'LESSTHAN', 'GREATERTHAN','LESSTHAN_EQUAL','GREATERTHAN_EQUAL'),
		('left', 'PLUS', 'MINUS'),
		('left', 'LSHIFT', 'RSHIFT'),
		('left', 'MULTIPLY', 'DIVIDE','MODULO'),
		('left', 'LPAREN', 'RPAREN')
)

def p_start(p):
		'''start : SourceFile'''
		p[0] = p[1]
		global root
		root = p[0]
		


# -----------------------TYPES---------------------------
def p_type(p):
		'''Type : TypeName
						| TypeLit'''
		p[0]=p[1]

def p_type_name(p):
		'''TypeName : TypeToken
								| QualifiedIdent'''
		p[0]=p[1]

def definedcheck(name):
	for scope in scopeStack[::-1]:
		if scopeDict[scope].retrieve(name) is not None:
			return True
	return False

def p_type_token(p):
		'''TypeToken : INT
								 | FLOAT
								 | BOOL
								 | STRING
								 | TYPE IDENTIFIER'''
		if len(p) == 2:
				p[0]=node()
				p[0].types.append(p[1])
				# define size for each
				if p[1]=='int' or p[1]=='float':
					p[0].size=[4]
					p[0].bytesize = 4
				elif p[1]=='bool':
					p[0].size=[1]
					p[0].bytesize = 4
				else:
					p[0].size = [32]
					p[0].bytesize = 32
					# maximum size of string set to 8 bytes
		else:
				if not definedcheck(p[2]):
					raise TypeError("Line "+str(p.lineno(1))+" : "+"TypeName " + p[2] + " not defined anywhere")
				else:
					p[0]=node()
					var = findinfo(p[2],0)
					p[0].types.append(var.type)
					
					
					
					p[0].size = [var.mysize]
					
					#TODO
					# coff = scopeDict[curScope].extra['curOffset']
					
					p[0].bytesize = var.mysize
					
					
					# scopeDict[curScope].updateExtra('curOffset',coff+var.mysize)

def p_type_lit(p):
		'''TypeLit : ArrayType
							 | ST StructType
							 | PointerType
							 | MapType
							 | SliceType'''
		if len(p)==2:
			p[0] = p[1]
		else:
			p[0] = p[2]

def p_S_T(p):
	'''ST : '''
	p[0] = p[-1]
	scopeDict[curScope].updateExtra('structname','type'+p[-1])
	scopeDict[curScope].updateExtra('structPscope',curScope)
	
	
	

# def p_type_opt(p):
#     '''TypeOpt : Type
#                | epsilon'''
#     p[0] = p[1]
# -------------------------------------------------------

def p_slice_type(p):
		'''SliceType : LSQUARE RSQUARE ElementType'''
		p[0] = p[3]
		#TODO
		print "SliceType : Not fully Implemented"


# ------------------ map type --------------------------

def p_map_type(p):
	'''MapType : MAP LSQUARE KeyType RSQUARE ElementType '''
	p[0] = p[3]
	p[0].code+=p[5].code
	#TODO
	p[0].types = ['m'] + p[3].types[0] + p[5].types[0]

def p_key_type(p):
	'''KeyType : Type'''
	p[0] = p[1]


# ------------------- ARRAY TYPE -------------------------

def p_array_type(p):
	'''ArrayType : LSQUARE ArrayLength RSQUARE ElementType'''
	p[0] = node()
	p[0].code = p[2].code + p[4].code
	p[0].bytesize = p[4].bytesize
	if p[2].types[0]!='int' and p[2].types[0]!='cint':
		raise IndexError("Line "+str(p.lineno(1))+" : "+"Index of array "+p[-1].idlist[0]+" is not integer")
	x = p[2].extra['operandValue'][0]
	p[0].bytesize *= int(x)
	s = p[4].types[0]
	if s.startswith('arr'):
		num = int(s[4])
		s = s[6:]
		p[0].types = ['arr_'+str(num+1)+'_'+s]
		if 'operandValue' in p[2].extra:
			p[0].limits = p[2].extra['operandValue']
			p[0].limits += p[4].limits
	else:
		p[0].types = ['arr_1_'+s]
		if 'operandValue' in p[2].extra:
			x = p[2].extra['operandValue']
			p[0].limits = x
			x = int(x[0])
	p[0].size = [int(x)] + p[4].size


def p_array_length(p):
	''' ArrayLength : I INT_LIT '''
	p[0]=node()
	p[0].extra['operandValue'] = [p[2]]
	p[0].types = ['cint']

def p_element_type(p):
	''' ElementType : Type '''
	p[0]=p[1]

# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
  '''StructType : FuncScope STRUCT LCURL FieldDeclRep RCURL EndScope'''
  p[0] = p[4]
  info = findinfo(p[-1],0)
  p[0].types = [info.type]
  scopeDict[curScope].updateAttr(p[-1],'mysize',p[4].bytesize)
  p[0].bytesize = p[4].bytesize

def p_func_scope(p):
  '''FuncScope : '''
  p[0] = node()
  # scopeDict[curScope].updateExtra('structPscope',curScope)
  x = curScope
  addscope(p[-1])
  scopeDict[curScope].updateExtra('structPscope',x)

def p_field_decl_rep(p):
	''' FieldDeclRep : FieldDeclRep FieldDecl Semi
									| epsilon '''
	if len(p) == 4:
		# addinstance(p[0],p[1],p[2])
		p[0] = p[1]
		p[0].types+=p[2].types
		p[0].code+=p[2].code
		p[0].idlist+=p[2].idlist
		p[0].bytesize += p[2].bytesize
		# p[0].extra['structname'] = p[-1]
	else:
		p[0]=p[1]

def p_field_decl(p):
  ''' FieldDecl : IdentifierList Type'''
  p[0] = p[1]
  sco = scopeDict[curScope].extra['structPscope']
  s = scopeDict[sco].extra['structname']
  
  if s in p[2].types:
    raise TypeError("Line "+str(p.lineno(1))+" : "+"Struct "+s[4:]+" recursively defind, not allowed")
  for i in range(len(p[0].idlist)):
    p[0].bytesize += p[2].bytesize
    x = p[0].idlist[i]
    info = findinfo(x)
    scopeDict[curScope].updateAttr(x,'type',p[2].types[0])
    scopeDict[curScope].extra['curOffset'] -= p[2].bytesize
    y = scopeDict[curScope].extra['curOffset']
    info.offset = y
    info.mysize = p[2].bytesize
    # scopeDict[curScope].updateExtra('curOffset',y+p[2].size[0])
    # p[0].bytesize +=p[2].size[0]

# ------------------POINTER TYPES--------------------------
def p_point_type(p):
		'''PointerType : MULTIPLY BaseType'''
		p[0] = p[2]
		p[0].size = p[0].size
		p[0].types[0]="*"+p[0].types[0]
		p[0].bytesize = 4
		

def p_base_type(p):
		'''BaseType : Type'''
		p[0]=p[1]
# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
    '''Signature : Parameters ResultOpt'''
    p[0]=p[1]
    p[0].retsize = p[2].retsize
    scopeDict[curScope].updateExtra('types',p[1].types)
    scopeDict[0].insert(p[-2],'sigType')
    info = findinfo(p[-2],0)
    if len(p[2].types)==0:
      scopeDict[0].updateAttr(p[-2],'ret','void')
      info.retsize = [0]
    else:
      for i in range(len(p[2].types)):
        scopeDict[0].updateAttr(p[-2],'ret',p[2].types[i])
    p[0].extra['fName'] = p[-2]
    if info.label==None:
      lnew = newlabel()
      scopeDict[0].updateAttr(p[-2],'label',lnew)
      scopeDict[0].updateAttr(p[-2],'child',scopeDict[curScope])
    p[0].types = p[2].types
    # parsize = -4 - scopeDict[curScope].extra['parOffset']
    
    
    
    p[0].bytesize = p[1].bytesize+p[2].bytesize
    # p[0].code.append(['move',str(p[0].bytesize),'0($fp)'])

def p_result_opt(p):
		'''ResultOpt : Result
								 | epsilon'''
		p[0]=p[1]

def p_result(p):
		'''Result : Parameters
							| Type'''
		p[0]=p[1]
		if not p[1].retsize :
			p[0].retsize = [p[1].bytesize]

def p_params(p):
		'''Parameters : LPAREN ParametersList RPAREN
									| LPAREN RPAREN'''
		if len(p) == 4:
			p[0] = p[2]
			if 'parOffset' not in scopeDict[curScope].extra:
				scopeDict[curScope].updateExtra('parOffset',4)
			# total_size=0
			l = len(p[0].idlist)-1
			for i in range(len(p[0].idlist)):
				ind = l-i
				
				x = p[0].idlist[ind]
				info = findinfo(x)
				y = scopeDict[curScope].extra['parOffset']
				z = info.mysize
				# total_size+=z
				info.offset = scopeDict[curScope].extra['parOffset']
				scopeDict[curScope].extra['parOffset'] += z

		else:
			p[0] = node()
			scopeDict[curScope].updateExtra('parOffset',4)

def p_param_list(p):
		'''ParametersList : ParameterDecl
											| ParametersList COMMA ParameterDecl'''
		if len(p) == 2:
			p[0]=p[1]
		else:
			p[0] = p[1]
			p[0].idlist += p[3].idlist
			p[0].types += p[3].types
			p[0].place += p[3].place
			p[0].bytesize+=p[3].bytesize
			p[0].retsize += p[3].retsize

def p_param_decl(p):
		'''ParameterDecl : IdentifierList Type
										 | Type'''
		p[0] = p[1]
		if len(p)==2:
			p[0].retsize.append(p[1].bytesize)
		if len(p) == 3:
			if (p[2].types[0]).startswith('arr') or (p[2].types[0]).startswith('*arr'):
				for x in p[1].idlist:
					scopeDict[curScope].updateExtra(x,p[2].limits)
					scopeDict[curScope].updateAttr(x,'type',p[2].types)
					scopeDict[curScope].updateAttr(x,'size',p[2].size)
					p[0].types += p[2].types
					info = findinfo(x)
					info.mysize = p[2].bytesize
					p[0].bytesize += p[2].bytesize
					info.listsize = p[2].limits + [str(p[2].size[len(p[2].size)-1])]
			else:
				for x in p[1].idlist:
					scopeDict[curScope].updateAttr(x,'type',p[2].types[0])
					scopeDict[curScope].updateAttr(x,'size',p[2].size)
					scopeDict[curScope].updateExtra(x,p[2].limits)
					p[0].types += p[2].types
					# p[0].types.append(p[2].types[0])
					info = findinfo(x)
					info.mysize = p[2].bytesize
					p[0].bytesize += p[2].bytesize
					# if pointer
					# if (p[2].types[0]).startswith('*'):
					# 	t = p[2].types[0]
					# 	for i in range(len(t)):
					# 		if t[i]!='*':
					# 			break
					# 	if t[i:] == 'int' or t[i:]=='float':
					# 		scopeDict[curScope].updateAttr(x,'size',[4])


#-----------------------BLOCKS---------------------------
def p_block(p):
		'''Block : LCURL StatementList RCURL'''
		p[0] = p[2]

def p_stat_list(p):
		'''StatementList : StatementRep'''
		p[0] = p[1]

def p_stat_rep(p):
		'''StatementRep : StatementRep Statement Semi
										| epsilon'''
		if len(p) == 4:
				p[0] = p[1]
				p[0].code += p[2].code
				
				p[0].idlist += p[2].idlist
		else:
				p[0] = node()
# -------------------------------------------------------


# ------------------DECLARATIONS and SCOPE------------------------
def p_decl(p):
	'''Declaration : ConstDecl
								 | TypeDecl
								 | VarDecl'''
	p[0] = p[1]

def p_toplevel_decl(p):
	'''TopLevelDecl : Declaration
									| FunctionDecl'''
	p[0] = p[1]
# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
		'''ConstDecl : CONST ConstSpec
								 | CONST LPAREN ConstSpecRep RPAREN'''
		if len(p) == 3:
				p[0]=p[2]
		else:
				p[0]=p[3]

def p_const_spec_rep(p):
		'''ConstSpecRep : ConstSpecRep ConstSpec Semi
										| epsilon'''
		if len(p) == 4:
				p[0]=p[1]
				p[0].code+=p[2].code
				p[0].bytesize += p[2].bytesize
		else:
				p[0]=p[1]

def p_const_spec(p):
		'''ConstSpec : IdentifierList TypeExprListOpt'''
		p[0] = node()
		p[0].code = p[1].code + p[2].code
		if len(p[1].place)!=len(p[2].place):
			raise ValueError("Line "+str(p.lineno(1))+" : "+"Error: Unequal number of identifiers and Expressions")
		for i in range(len(p[1].place)):
			x = p[1].idlist[i]
			info = findinfo(x)
			p[0].code.append(['=',p[1].place[i],p[2].place[i]])
			p[1].place[i] = p[2].place[i]
			p[0].bytesize += p[2].bytesize
			info.mysize = p[2].bytesize
			scopeDict[curScope].extra['curOffset'] -= p[2].bytesize
			info.offset = scopeDict[curScope].extra['curOffset']
			scope = findscope(x)
			# scopeDict[scope].updateAttr(x,'place',p[1].place[i])
			if p[2].types[i]==i:
				raise TypeError("Line "+str(p.lineno(1))+" : "+'Type of ' + p[1].idlist[i] + ' does not match that of expr')
			scopeDict[scope].updateAttr(x,'type','c'+p[2].types[i])


def p_type_expr_list(p):
		'''TypeExprListOpt : Type EQUALS ExpressionList'''
		if len(p) == 4:
			p[0]=p[3]
			p[0].bytesize = p[1].bytesize
			flag=0
			for i in range(len(p[0].place)):
				if not equalcheck(p[1].types[0],p[3].types[i]):
					p[0].types[i] = i
					flag=1
				else:
					p[0].types[i]=p[1].types[0]


def p_identifier_list(p):
		'''IdentifierList : IDENTIFIER 
											| IdentifierRep'''
		if hasattr(p[1],'idlist'):
			p[0]=p[1]
		else:
			p[0]=node()
			# cv = newcvar()
			# cname[p[1]] = cv
			p[0].idlist+=[p[1]]
			if checkid(p[1],"e"):
				raise NameError("Line "+str(p.lineno(1))+" : "+p[1]+" : This name already exists")
			else:
				scopeDict[curScope].insert(p[1],None)
				v = newvar()
				p[0].place = [v]
				scopeDict[curScope].updateAttr(p[1],'place',v)

def p_identifier_rep(p):
		'''IdentifierRep : IdentifierRep COMMA IDENTIFIER
										 | IDENTIFIER COMMA IDENTIFIER'''
		if hasattr(p[1],'idlist'):
			p[0]=p[1]
			p[0].idlist = p[0].idlist + [p[3]]
			if checkid(p[3],"e"):
				raise NameError("Line "+str(p.lineno(1))+" : "+p[3]+" : This name already exists")
			else:
				scopeDict[curScope].insert(p[3],None)
				v = newvar()
				cname[p[1]] = v
				p[0].place = p[0].place + [v]
				scopeDict[curScope].updateAttr(p[3],'place',v)
		else:
			p[0]=node()
			p[0].idlist = [p[1]] + [p[3]]
			if checkid(p[1],"e") or checkid(p[3],"e"):
				if checkid(p[1],"e"):
					raise NameError("Line "+str(p.lineno(1))+" : "+p[1]+" : This name already exists")
				else:
					raise NameError("Line "+str(p.lineno(1))+" : "+p[3]+" : This name already exists")
			else:
				scopeDict[curScope].insert(p[1],None)
				scopeDict[curScope].insert(p[3],None)
				v1 = newvar()
				v2 = newvar()
				p[0].place = [v1] + [v2]
				scopeDict[curScope].updateAttr(p[1],'place',v1)
				scopeDict[curScope].updateAttr(p[3],'place',v2)


def p_expr_list(p):
		'''ExpressionList : Expression ExpressionRep'''
		if len(p) == 3:
			p[0]=p[2]
			p[0].code = p[1].code+p[0].code
			p[0].place = p[1].place + p[0].place
			p[0].types = p[1].types + p[0].types
			p[0].idlist = p[1].idlist + p[0].idlist
			p[0].bytesize = p[1].bytesize + p[2].bytesize
			if 'AddrList' not in p[1].extra:
				p[1].extra['AddrList'] = ['None']
			p[0].extra['AddrList'] += p[1].extra['AddrList']
			p[0].extra['ParamSize'] = [p[1].bytesize] + p[2].extra['ParamSize']

def p_expr_rep(p):
		'''ExpressionRep : ExpressionRep COMMA Expression
										 | epsilon'''
		if len(p) == 4:
				p[0]=p[1]
				p[0].code+=p[3].code
				p[0].types+=p[3].types
				p[0].place+=p[3].place
				p[0].idlist += p[3].idlist
				p[0].bytesize += p[3].bytesize
				if 'AddrList' not in p[3].extra:
					p[3].extra['AddrList'] = ['None']
				p[0].extra['AddrList'] += p[3].extra['AddrList']
				p[0].extra['ParamSize'] += [p[3].bytesize]
		else:
				p[0]=p[1]
				p[0].extra['AddrList'] = []
				p[0].extra['ParamSize'] = []
# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
		'''TypeDecl : TYPE TypeSpec
								| TYPE LPAREN TypeSpecRep RPAREN'''
		if len(p) == 5:
				p[0] = p[3]
		else:
				p[0] = p[2]

def p_type_spec_rep(p):
		'''TypeSpecRep : TypeSpecRep TypeSpec Semi
									 | epsilon'''
		if len(p) == 4:
				p[0] = node()
		else:
				p[0]=p[1]

def p_type_spec(p):
		'''TypeSpec : AliasDecl
								| TypeDef'''
		p[0]=p[1]

def p_alias_decl(p):
		'''AliasDecl : IDENTIFIER EQUALS Type'''
		if checkid(p[1],'andsand'):
			raise NameError("Line "+str(p.lineno(1))+" : "+"Name "+p[1]+" already defined")
		else:
			
			scopeDict[curScope].insert(p[1],p[3].types[0])
		p[0]=node()
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
		'''TypeDef : IDENTIFIER Type'''
		if checkid(p[1],'andsand'):
			raise NameError("Line "+str(p.lineno(1))+" : "+"Name "+p[1]+" already defined")
		else:
			
			
			scopeDict[curScope].insert(p[1],p[2].types[0])
		p[0]=node()
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
		'''VarDecl : VAR VarSpec
							 | VAR LPAREN VarSpecRep RPAREN'''
		if len(p) == 3:
				p[0] = p[2]
		else:
				p[0] = p[3]

def p_var_spec_rep(p):
		'''VarSpecRep : VarSpecRep VarSpec Semi
									| epsilon'''
		if len(p) == 4:
				p[0] = p[1]
				p[0].code+=p[2].code
				p[0].bytesize += p[2].bytesize
				
		else:
				p[0]=p[1]

def p_var_spec(p):
	'''VarSpec : IdentifierList Type ExpressionListOpt'''
	if len(p[3].place)==0:
		a=0
		if 'malloc' in p[3].extra:
			if p[2].types[0].startswith('*'):
				a=1
			else:
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Malloc done to a non-pointer type")
				return
		p[0]=p[1]
		p[0].code+=p[2].code
		# p[0].bytesize = p[2].bytesize
		for i in range(len(p[1].idlist)):
			x = p[1].idlist[i]
			s = findscope(x)
			info = findinfo(x)
			#For arraysDeclaration
			if (p[2].types[0]).startswith('arr'):
				scopeDict[curScope].updateExtra(x,p[2].limits)
				scopeDict[s].updateAttr(x,'type',p[2].types[0])
				scopeDict[s].updateAttr(p[1].idlist[i],'size',p[2].size)
				p[0].bytesize += p[2].bytesize
				info.mysize = p[2].bytesize
				scopeDict[curScope].extra['curOffset'] -= p[2].bytesize
				info.offset = scopeDict[curScope].extra['curOffset']
			elif a==1:      #  malloc
				if p[2].types[0]=='*arr':
					raise TypeError("Line "+str(p.lineno(1))+" : "+"Malloc for array must be in a loop")
				p[0].code.append(['call_malloc',x,str(p[3].bytesize)])
				scopeDict[s].updateAttr(x,'type',p[2].types)
			else:
				scopeDict[s].updateAttr(x,'type',p[2].types[0])
				p[0].bytesize += p[2].bytesize
				scopeDict[s].updateAttr(p[1].idlist[i],'size',p[2].size)
				scopeDict[curScope].updateExtra(x,p[2].limits)
				info.mysize = p[2].bytesize
				scopeDict[curScope].extra['curOffset'] -= p[2].bytesize
				info.offset = scopeDict[curScope].extra['curOffset']
				# p[0].code.append(['=',x,p[1].place[i]])
				
				
		return
	
	p[0]=node()
	p[0].code = p[1].code + p[3].code
	if len(p[1].place)!=len(p[3].place):
		raise ValueError("Line "+str(p.lineno(1))+" : "+"Mismatch in number of expressions assigned to variables")

	for i in range(len(p[1].place)):
		x = p[1].idlist[i]
		if p[2].types[0]=='float' or p[2].types[0]=='cfloat':
			eq = 'f='
		else:
			eq = '='
		# p[1].place[i] = p[3].place[i]
		scope = findscope(x)
		info = findinfo(x)
		p[0].code.append([eq,p[1].place[i],p[3].place[i]])
		scopeDict[scope].updateAttr(x,'place',p[1].place[i])
		scopeDict[scope].updateAttr(x,'type',p[2].types[0])
		p[0].bytesize += p[2].bytesize
		scopeDict[curScope].extra['curOffset'] -= p[2].bytesize
		info.offset = scopeDict[curScope].extra['curOffset']
		info.mysize = p[2].bytesize
		#pointer case
		if (p[2].types[0]).startswith('arr') or (p[2].types[0]).startswith('*arr'):
			scopeDict[scope].updateAttr(x,'size',p[2].size)
			scopeDict[curScope].updateExtra(x,p[2].limits)

		if type(p[3].types[i]) is list:
			s = p[3].types[i][0]
		else:
			s = p[3].types[i]
		
		if not equalcheck(p[2].types[0],s):
			raise TypeError("Line "+str(p.lineno(1))+" : "+"Type of "+ x + " does not match that of expr")


def p_expr_list_opt(p):
		'''ExpressionListOpt : EQUALS ExpressionList
												 | epsilon
												 | EQUALS MALLOC LPAREN I INT_LIT RPAREN'''
		if len(p) == 3:
				p[0] = p[2]
		elif len(p) == 7:
			p[0] = node()
			p[0].bytesize = 4*int(p[5])
			p[0].extra['malloc'] = 1
		else:
			p[0]=p[1]
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECL-------------
def p_short_var_decl(p):
	''' ShortVarDecl : IDENTIFIER SHORT_ASSIGNMENT Expression '''
	p[0] = node()
	if checkid(p[1],'e'):
		raise NameError("Line "+str(p.lineno(1))+" : "+"Variable"+p[1]+"already exists.")
	else:
		scopeDict[curScope].insert(p[1],None)
	v = newvar()
	# v_decl(v,curScope)
	p[0].code = p[3].code
	p[0].code.append(['=',v,p[3].place[0]])
	x = p[3].types[0]
	info = findinfo(p[1])
	if x=='int' or x=='cint' or x=='float' or x=='cfloat' or x=='bool' or x=='cbool':
		p[0].bytesize = 4
	elif x=='string':
		p[0].bytesize = 32
	if x.startswith('c'):
		info.type = x[1:]
	else:
		info.type = x
	scopeDict[curScope].extra['curOffset'] -= p[0].bytesize
	info.offset = scopeDict[curScope].extra['curOffset']
	info.mysize = p[0].bytesize
	p[0].place = [v]
	p[0].types = p[3].types
	scopeDict[curScope].updateAttr(p[1],'place',v)
	# scopeDict[curScope].updateAttr(p[1],'type',p[3].types[0])

# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
	'''FunctionDecl : FUNC FunctionName CreateScope Function EndScope
					| FUNC FunctionName CreateScope Signature EndScope'''
	p[0]=node()
	info = findinfo(p[2])
	info.name = p[2]
	if len(p[4].code):
		global mainFunc
		if mainFunc:
			mainFunc = False
			# p[0].code = [["goto","main"]]
		p[0].code.append(['label',p[2]])
		x = scopeDict[info.child.val].extra['funcOffset']
		info.funcsize = x
		p[0].code.append(['$sp',str(x)])
		# p[0].code.append()
		# if p[2]!='main':
			# p[0].code.append(['movs',"%r9",'0($fp)'])
		info.mysize = p[4].bytesize
		p[0].code += p[4].code
	p[0].idlist += [p[2]]
	p[0].retsize = p[4].retsize

def p_create_scope(p):
	'''CreateScope : '''
	addscope()

def p_end_scope(p):
	'''EndScope : '''
	endscope()

def p_func_name(p):
	'''FunctionName : IDENTIFIER'''
	p[0] = p[1]

def checksignature(name):
	for scope in scopeStack[::-1]:
		if scopeDict[scope].retrieve(name) is not None:
			info = scopeDict[scope].retrieve(name)
			if info.type=="sigType":
				return True
	return False

def p_func(p):
		'''Function : Signature RetTypeSet FunctionBody'''
		p[0] = p[3]
		p[0].bytesize = p[1].bytesize
		p[0].retsize = p[1].retsize
		scopeDict[curScope].updateExtra('curOffset',0)
		for i in range(len(p[1].idlist)):
			x = p[1].idlist[i]
			info = findinfo(x)
		if checksignature(p[-2]):
			if p[-2]=="main":
				scopeDict[0].updateAttr('main','label','main')
				scopeDict[0].updateAttr('main','child',scopeDict[curScope])
			info = findinfo(p[-2])
			info.type = 'func'
		else:
			raise NameError("Line "+str(p.lineno(1))+" : "+'No Signature found for '+p[-2])


def p_ret_type_set(p):
	'''RetTypeSet : '''
	fname = p[-1].extra['fName']
	info = findinfo(fname)
	info.mysize = p[-1].bytesize
	info.retsize = p[-1].retsize
	scopeDict[curScope].updateExtra('fName',fname)
	if len(p[-1].types)==1:
		scopeDict[curScope].updateExtra('retType',p[-1].types[0])
	elif len(p[-1].types)>1:
		scopeDict[curScope].updateExtra('retType',p[-1].types)
	else:
		scopeDict[curScope].updateExtra('retType','void')

def p_func_body(p):
		'''FunctionBody : Block'''
		p[0] = p[1]
		scopeDict[curScope].extra['funcOffset'] =  scopeDict[curScope].extra['curOffset']
		x = scopeDict[curScope].extra['curOffset']
		s = scopeDict[curScope].extra['fName']
		# p[0].code.append(['$sp',str(-x)])
		p[0].code.append(['jr','$ra',s])
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
		'''Operand : Literal
							 | OperandName
							 | LPAREN Expression RPAREN'''
		if len(p) == 2:
				p[0] = p[1]
		else:
				p[0] = p[2]

def p_literal(p):
		'''Literal : BasicLit'''
		p[0] = p[1]

stringNum = 0
def p_basic_lit(p):
  '''BasicLit : I INT_LIT
              | F FLOAT_LIT
              | C IMAGINARY_LIT
              | B BOOL_LIT
              | S STRING_LIT'''
  p[0]=p[1]
  
  if p[1].types[0]=='cstring':
    global stringNum
    c = 'temp_str'+str(stringNum)
    stringNum += 1
    scopeDict[curScope].insert(c,None)
    info = findinfo(c,curScope)
    info.type = 'string'
    scopeDict[curScope].extra['curOffset'] -= 32
    info.offset = scopeDict[curScope].extra['curOffset']
    info.mysize = 32
    p[0].code.append(["=",c,p[2]])
  elif p[1].types[0]=='cfloat':
    c = newconst('float')
    p[0].code.append(["f=",c,p[2]])
  else:
    c = newconst()
    p[0].code.append(["=",c,p[2]])
  p[0].place.append(c)
  p[0].extra['operandValue'] = [p[2]]

def p_B(p):
	'''B : '''
	p[0]=node()
	p[0].types.append('cbool')
	p[0].bytesize = 4

def p_I(p):
	'''I : '''
	p[0]=node()
	p[0].types.append('cint')
	p[0].bytesize = 4

def p_F(p):
	'''F : '''
	p[0]=node()
	p[0].types.append('cfloat')
	p[0].bytesize = 4

def p_C(p):
	'''C : '''
	p[0]=node()
	p[0].types.append('ccomplex')
	p[0].bytesize = 4

def p_S(p):
	'''S : '''
	p[0]=node()
	p[0].types.append('cstring')
	p[0].bytesize = 32

def p_operand_name(p):
	'''OperandName : IDENTIFIER'''
	if not definedcheck(p[1]):
		raise NameError("Line "+str(p.lineno(1))+" : "+"identifier " + p[1] + " is not defined")
	p[0] = node()
	info = findinfo(p[1])
	if info.type == 'sigType':
		if len(info.retsize)==0:
			p[0].bytesize = 0
		else:
			p[0].bytesize = info.retsize[0]
	else:
		p[0].bytesize = info.mysize
	if type(info.type) is list:
		s = info.type[0]
	else:
		s = info.type
	if s=='func' or s=='sigType':
		p[0].types = [info.retType]
		p[0].place.append(info.label)
	else:
		p[0].types = [s]
		p[0].place.append(info.place)
		p[0].extra['layerNum'] = 0
		p[0].extra['operand'] = p[1]
		if info.listsize is not None:
			p[0].size = info.listsize
		else:
			for i in range(len(s)):
				if s[i]!='*':
					break;
			if s[i:]=='int':
				
				p[0].size = ['4']
	p[0].idlist = [p[1]]
		
# ---------------------------------------------------------


# -------------------QUALIFIED IDENTIFIER----------------
def packageimport(name):
	for scope in scopeStack[::-1]:
		if scopeDict[scope].retrieve(name) is not None:
			info = scopeDict[scope].retrieve(name)
			if info['type'] == "package":
					return True

	return False

def p_qualified_ident(p):
		'''QualifiedIdent : IDENTIFIER DOT TypeName'''
		p[0] = node()
		if packageimport(p[1]):
			raise NameError("Line "+str(p.lineno(1))+" : "+"package"+p[1]+"not included")
		p[0].types.append(p[1]+p[2]+p[3].types[0])


# -------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
  '''PrimaryExpr : Operand
                 | PrimaryExpr DOT IDENTIFIER
                 | Conversion
                 | PrimaryExpr LSQUARE Expression RSQUARE
                 | PrimaryExpr Slice
                 | PrimaryExpr TypeAssertion
                 | PrimaryExpr LPAREN ExpressionListTypeOpt RPAREN'''
  if len(p) == 2:
    p[0] = p[1]
  # Arrays: ----------------------------------------
  elif p[2]=='[':
    p[0] = p[1]
    p[0].code+=p[3].code
    name = p[1].extra['operand']
    info = findinfo(name)
    lsize = info.listsize
    s = info.type
    if type(s) is list:
      s = s[0]
    l = s.split('_')
    if p[3].types[0]!='int' and p[3].types[0]!='cint':
      raise IndexError("Line "+str(p.lineno(1))+" : "+"Array index of array " + p[1].extra['operand'] + " is not integer")
    # check on index range
    if (p[1].types[0]).startswith('*arr'):
    	lsize = lsize[1:]
    flag = 0
    if p[0].extra['layerNum']==0:
      c = newconst()
      p[0].code.append(['=',c,str(info.offset)])
      p[0].place = [c]
    elif p[0].extra['layerNum']==-1:
    	flag = 1
    	p[0].extra['layerNum'] = 0

    k = p[1].extra['layerNum']
    if p[1].extra['layerNum'] == len(lsize)-1:
      raise IndexError("Line "+str(p.lineno(1))+" : "+'Dimension of array '+p[1].extra['operand'] + ' doesnt match')
    if 'operandValue' in p[3].extra:
      z = p[3].extra['operandValue'][0]
      y = scopeDict[curScope].extra[p[1].extra['operand']]
      if z>=y[k]:
        raise IndexError("Line "+str(p.lineno(1))+" : "+"Array "+ p[1].extra['operand'] +" out of Bounds "+" at level = "+str(k))
    
    v1 = newvar()
    scopeDict[curScope].insert(v1,None)
    vinfo = findinfo(v1)
    scopeDict[curScope].extra['curOffset'] -= 4
    vinfo.offset = scopeDict[curScope].extra['curOffset']
    vinfo.mysize = 4
    p[0].code.append(['=',v1,p[3].place[0]])
    for i in lsize[p[1].extra['layerNum']+1:]:
      c1 = newconst()
      p[0].code.append(['=',c1,i])
      p[0].code.append(['*=',v1,c1])

    # Adding previous offset
    p[0].code.append(['+',v1,v1,p[0].place[0]])

    p[0].place = [v1]
    if p[1].extra['layerNum'] == len(lsize)-2:
      if flag==0:
      	p[0].code.append(['mem+',v1,'$fp'])
      p[0].place = ['addr_'+v1]
    p[0].extra['AddrList'] = [v1]
    if k==len(lsize)-2:
      p[0].types = [l[2]]
    else:
      x =  int(l[1])-k-1
      p[0].types = [l[0]+'_'+str(x)+'_'+l[2]]
    p[0].extra['layerNum'] += 1
    p[0].extra['arrayvar'] = v1
    
  # -------------------function case ------------------------
  elif p[2]=='(':
    p[0]=p[1]
    p[0].code+=p[3].code
    x = p[1].idlist[0]
    info = findinfo(p[1].idlist[0],0)
    functionDict = info.child
    if len(functionDict.extra['types'])!=len(p[3].place):
      raise IndexError("Line "+str(p.lineno(1))+" : "+"Function "+x+" passed with Unequal number of arguments")
    paramTypes = functionDict.extra['types']
    if len(p[3].place):
      for i in range(len(p[3].place)):
        if not equalcheck(paramTypes[i],p[3].types[i]):
          raise TypeError("Line "+str(p.lineno(1))+" : "+"Type Mismatch in "+p[1].idlist[0])

    # Checking Return Type
    name = p[1].idlist[0]
    info.label = name
    curval = scopeDict[curScope].extra['curOffset']
    start = curval
    funcinfo = findinfo(p[1].idlist[0])
    funcsize = funcinfo.mysize
    start -= 4
    return_off = start
    if len(info.retType)==1:
      if len(info.retsize):
        start -= info.retsize[0]
      curstart = start
      for i in range(len(p[3].place)):
        start -= p[3].extra['ParamSize'][i]
      diff = start - curval -4
      p[0].code.append(['addi','$sp','$sp',str(diff)])
      p[0].code.append(['push','$ra',str(return_off)])
      start = curstart
      for i in range(len(p[3].place)):
      	start -= p[3].extra['ParamSize'][i]
        p[0].code.append(['push',p[3].place[i],str(p[3].extra['ParamSize'][i]),str(start)])
      start -= 4
      p[0].code.append(['push',str(start),str(start)])
      p[0].code.append(['addi','$fp','$fp',str(start)])
      p[0].code.append(['jal',info.label])
      p[0].code.append(['addi','$fp','$fp',str(-start)])
      p[0].code.append(['loadra','$ra',str(scopeDict[curScope].extra['curOffset']-4)+'($fp)'])
      flag=0
      if info.retType[0]=='void':
        flag=1
      if flag==0:
        scopeDict[curScope].extra['curOffset'] -= 4
        v1 = newvar()
        v_decl(v1,curScope,info.retsize[0])
        vinfo = findinfo(v1)
        p[0].place = [v1]
        return_off -= info.retsize[0]
        vinfo.type =  p[1].types[0]
        # p[0].code.append(['memt',str(return_off),v1,str(info.retsize[0])])
      p[0].code.append(['addi','$sp','$sp',str(-diff)])
      p[0].types = p[1].types[0]
    else:
      p[0].place = []
      p[0].types = info.retType
      for i in range(len(info.retType)):
        start-=info.retsize[i]
      #   p[0].code.append(['push','ret'+str(i+1),str(info.retsize[i])])
      curstart = start
      for i in range(len(p[3].place)):
        start -= p[3].extra['ParamSize'][i]
      diff = start - curval -4
      p[0].code.append(['addi','$sp','$sp',str(diff)])
      p[0].code.append(['push','$ra',str(return_off)])
      start = curstart
      for i in range(len(p[3].place)):
      	start -= p[3].extra['ParamSize'][i]
        p[0].code.append(['push',p[3].place[i],p[3].extra['ParamSize'][i],str(start)])
      start-=4
      p[0].code.append(['push',str(start),str(start)])
      p[0].code.append(['addi','$fp','$fp',str(start)])
      p[0].code.append(['jal',info.label])
      p[0].code.append(['addi','$fp','$fp',str(-start)])
      p[0].code.append(['loadra','$ra',str(scopeDict[curScope].extra['curOffset']-4)+'($fp)'])
      scopeDict[curScope].extra['curOffset'] -= 4
      for i in range(len(info.retType)):
        s = newvar()
        v_decl(s,curScope,info.retsize[i])
        return_off -= info.retsize[i]
        sinfo = findinfo(s)
        sinfo.type = [info.retType[i]]
        # p[0].code.append(['memt',str(return_off),s,info.retsize[i]])
        p[0].place.append(s)
      p[0].code.append(['addi','$sp','$sp',str(-diff)])

  # ------------------   SELECTOR  -------------------------
  elif len(p) == 4:
    p[0] = p[1]
    x = p[1].idlist[0]
    info = findinfo(x)
    t = info.type
    if type(t) is list:
    	t = str(t[0])

    if t.startswith('arr'):
      l = t.split('_')
      t = l[2][4:]
    # Pointer case --- to be handled -->
    elif t[0]=='*':
      if t[1:5]!='type':
        raise TypeError("Line "+str(p.lineno(1))+" : "+t+" does not have any attribute")
        return
      # if x not in scopeDict[curScope].extra:
      #   raise NameError("Line "+str(p.lineno(1))+" : "+x+" is not set")
      t = t[5:]
    else:
      t = t[4:]

    sinfo = findinfo(t)
    sScope = sinfo.child
    if p[3] not in sScope.table:
      raise NameError("Line "+str(p.lineno(1))+" : "+"identifier " + p[3]+ " is not defined inside the struct " + x)
    # varname = x+'.'+p[3]
    # if info.type.startswith('arr'):
    # 	varname = x+'_'+p[1].place[0]+'.'+p[3]
    if not checkid(x,'e',1):
      raise NameError("Line "+str(p.lineno(1))+" : "+x+" does not exist")
    
    v = newvar()
    varinfo = sScope.retrieve(p[3])
    attr_type = varinfo.type
    varname = v
    v_decl(v,curScope,varinfo.mysize)
    vinfo = findinfo(varname)
    vinfo.type = p[0].types[0]				#  to check
    # p[0].types = [varinfo.type]
    # p[0].place = [v]

    # -------------------   a.next.age  ---------------------
    if (info.type).startswith('*'):
    	c = newconst()
    	curoff = (sinfo.mysize + varinfo.offset)
    	p[0].code.append(['=',c,str(curoff)])
    	p[0].code.append(['+',v,p[1].place[0],c])
    	p[0].types = [varinfo.type]
    	p[0].place = ['addr_'+v]
    #  	----------------    a[i].next, a[i].age  ------------------------- 
    elif (info.type).startswith('arr'):
        # pl = p[1].extra['arrayvar']
        x = p[1].place[0]
        x=x[5:]
        p[0].types = [varinfo.type]
        vinfo.type = attr_type
        p[0].place = ['addr_'+v]
        curoff = sinfo.mysize + varinfo.offset
        c = newconst()
        p[0].code.append(['=',c,str(curoff)])
        p[0].code.append(['+',v,x,c])
    # ----------------------  a.age, a.next    ---------------
    else:
        curoff = (sinfo.mysize + varinfo.offset)
        i = p[1].idlist[0]
        i_info = findinfo(i)
        c = newconst()
        c1 = newconst()
        p[0].types = [attr_type]
        vinfo.type = attr_type
        p[0].code.append(['=',c,str(i_info.offset)])
        p[0].code.append(['=',c1,str(curoff)])
        p[0].code.append(['+',v,c,c1])
        p[0].code.append(['mem+',v,'$fp'])
        p[0].place = ['addr_'+v]
    p[0].idlist = [varname]
  else:
    
    if not len(p[3].place):
      p[0] =node()


def p_slice(p):
		'''Slice : LSQUARE ExpressionOpt COLON ExpressionOpt RSQUARE
						 | LSQUARE ExpressionOpt COLON Expression COLON Expression RSQUARE'''
		print "Slice not Implemented"
		if len(p) == 6:
				p[0] = node()
		else:
				p[0] = node()

def p_type_assert(p):
		'''TypeAssertion : DOT LPAREN Type RPAREN'''
		p[0] = p[3]
		print "Type Assertion Not Implemented (Interface also not Implemented)"

def p_expr_list_type_opt(p):
		'''ExpressionListTypeOpt : ExpressionList
														 | epsilon'''
		p[0] = p[1]

def p_expr(p):
		'''Expression : UnaryExpr
									| Expression COMPARE_OR Expression
									| Expression COMPARE_AND Expression
									| Expression EQEQ Expression
									| Expression NOTEQUALS Expression
									| Expression LESSTHAN Expression
									| Expression GREATERTHAN Expression
									| Expression LESSTHAN_EQUAL Expression
									| Expression GREATERTHAN_EQUAL Expression
									| Expression OR Expression
									| Expression XOR Expression
									| Expression ANDXOR Expression
									| Expression DIVIDE Expression
									| Expression MODULO Expression
									| Expression LSHIFT Expression
									| Expression RSHIFT Expression
									| Expression PLUS Expression
									| Expression MINUS Expression
									| Expression MULTIPLY Expression
									| Expression AND Expression'''
		if len(p)==2:
			p[0]=p[1]
		else:

			p[0]=node()
################################### pointer = NULL ###################################
			

			if p[2]=='==' or p[2]=='!=':
				if p[1].types[0].startswith('*'):
					if p[3].types[0]=='*NULL':
						c = newconst()
						v = newvar()
						v_decl(v,curScope)
						p[0].code.append(['=',c,'0'])
						# p[0].code.append(['=',p[1].place[0],c])
						p[0].code.append([p[2],v,p[1].place[0],c])
						p[0].types = ['bool']
						p[0].place = [v]
						return
################################### pointer = NULL ###################################

			p[0].code = p[1].code + p[3].code
			p[0].idlist = p[1].idlist + p[3].idlist
			p[0].bytesize = p[1].bytesize
			if (p[2]=='<<' or p[2]=='>>' or p[2]=='^' or p[2]=='&^' or p[2]=='%' or p[2]=='|' or p[2]=='&') and ((p[3].types[0]!='int' and p[3].types[0]!='cint') or (p[1].types[0]!='int' and p[1].types[0]!='cint')):
				raise TypeError("Line "+str(p.lineno(1))+" : "+"RHS/LHS of "+p[2]+" is not integer")
			if p[1].types[0]=='float' or p[3].types[0]=='float' or p[1].types[0]=='cfloat' or p[3].types[0]=='cfloat':
				op = 'f' + p[2]
			else:
				op = p[2]
			if not opTypeCheck(p[1].types[0],p[3].types[0],'.'):
				if (p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/') and (p[1].types[0]=='cint'or p[1].types[0]=='int') and (p[3].types[0]=='cfloat'or p[3].types[0]=='float'):
					x=1
				elif (p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/') and (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]=='cfloat'or p[1].types[0]=='float'):
					x=2
				elif (p[3].types[0]=='*NULL'):
					x=3
				else:
					raise TypeError("Line "+str(p.lineno(1))+" : "+"Types of expressions does not match")
			else:
				p[0].types=p[1].types
			if p[2]=='==' or p[2]=='!=' or p[2]=='<' or p[2]=='>' or p[2]=='<=' or p[2]=='>=':
				p[0].types = ['bool']


			v = newvar()
			scopeDict[curScope].insert(v,None)
			vinfo = findinfo(v)
			scopeDict[curScope].extra['curOffset'] -= 4
			vinfo.offset = scopeDict[curScope].extra['curOffset']
			vinfo.mysize = 4
			if p[2]=='*':
				p[0].code.append([op,v,p[1].place[0],p[3].place[0]])
			elif p[2]=='&&':
				p[0].code.append(['&',v,p[1].place[0],p[3].place[0]])
			elif p[2]=='||':
				p[0].code.append(['|',v,p[1].place[0],p[3].place[0]])
			elif p[2]=='<<':
				p[0].code.append(['=',v,p[1].place[0]])
				p[0].code.append(['<<=',v,p[3].place[0]])
			elif p[2]=='>>':
				p[0].code.append(['=',v,p[1].place[0]])
				p[0].code.append(['>>=',v,p[3].place[0]])
			elif (p[2]=='+'or p[2]=='-') and (p[1].types[0]=='cint'or p[1].types[0]=='int') and (p[3].types[0]).startswith('*'):
				t = newvar()
				scopeDict[curScope].insert(t,None)
				vinfo = findinfo(t)
				scopeDict[curScope].extra['curOffset'] -= 4
				vinfo.offset = scopeDict[curScope].extra['curOffset']
				vinfo.mysize = 4
				p[0].code.append(['=',t,'4'])
				p[0].code.append(['*',t,t,p[1].place[0]])
				p[0].code.append(['+',v,t,p[3].place[0]])
			elif (p[2]=='+'or p[2]=='-') and (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]).startswith('*'):
				t = newvar()
				scopeDict[curScope].insert(t,None)
				vinfo = findinfo(t)
				scopeDict[curScope].extra['curOffset'] -= 4
				vinfo.offset = scopeDict[curScope].extra['curOffset']
				vinfo.mysize = 4
				p[0].code.append(['=',t,'4'])
				p[0].code.append(['*',t,t,p[3].place[0]])
				p[0].code.append(['+',v,t,p[1].place[0]])
			elif p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/':
				if (p[1].types[0]=='cint'or p[1].types[0]=='int') and (p[3].types[0]=='cfloat'or p[3].types[0]=='float'):
					p[0].code.append(['typecast','float',p[1].place[0]])
					p[1].types = ['float']
					p[0].types = ['float']
					p[0].code.append([op,v,p[1].place[0],p[3].place[0]])
				elif (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]=='cfloat'or p[1].types[0]=='float'):
					p[0].code.append(['typecast','float',p[3].place[0]])
					p[3].types = ['float']
					p[0].types = ['float']
					p[0].code.append([op,v,p[1].place[0],p[3].place[0]])
				else:
					p[0].code.append([op,v,p[1].place[0],p[3].place[0]])
			else:
				p[0].code.append([p[2],v,p[1].place[0],p[3].place[0]])
			p[0].place = [v]

			if not opTypeCheck(p[1].types[0],p[3].types[0],p[2]):
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Expression types dont match on both side of operation "+p[2])


def p_expr_opt(p):
		'''ExpressionOpt : Expression
										 | epsilon'''
		p[0]=p[1]

def p_unary_expr(p):
		'''UnaryExpr : PrimaryExpr
					 | UnaryOp UnaryExpr
					 | NOT UnaryExpr
					 | NULL'''
		if p[1]=='null':
			p[0] = node()
			p[0].types = ['*NULL']
		elif len(p) == 2:
				p[0] = p[1]
		elif p[1] == "!":
			p[0] = p[2]
			v = newvar()
			scopeDict[curScope].insert(v,None)
			vinfo = findinfo(v)
			scopeDict[curScope].extra['curOffset'] -= 4
			vinfo.offset = scopeDict[curScope].extra['curOffset']
			vinfo.mysize = 4
			p[0].code.append(["!",v,p[2].place[0]])
			p[0].place = [v]
		else:
			p[0] = p[2]
			if p[1][0]=='&' or p[1][0]=='*':
				p[0].bytesize = 4
			v = newvar()
			v_decl(v,curScope)
			if p[1][0]=='+' or p[1][0]=='-':
				if p[2].types[0]=='float' or p[2].types[0]=='float':
					op = 'f' + p[1][0]
					op1 = 'f='
					c = newconst('float')
				else:
					op = p[1][0]
					op1 = '='
					c = newconst()
				p[0].code.append([op1,c,0])
				p[0].code.append([op,v,c,p[2].place[0]])
				p[0].place=[v]
			elif p[1][0]=='*':
				# p[0].code.append(['load',v,p[2].place[0]])
				# v = newvar()
				# v_decl(v,curScope)
				# p[0].code.append(['=',v,p[2].place[0]])
				# p[0].code.append(['mem+',v,'$fp'])
				# if (p[2].place[0]).startswith('addr_'):
				# 	p[0].place = [p[2].place[0]]
				# else:
				v=newvar()
				v_decl(v,curScope)
				p[0].code.append(['=',v,p[2].place[0]])
				# p[0].place = ['addr_'+p[2].place[0]]
				if (p[2].types[0]).startswith('*arr'):
					p[0].place = [v]
				else:
					p[0].place = ['addr_'+v]
				if p[2].types[0][0]!='*':
					raise TypeError("Line "+str(p.lineno(1))+" : "+"Cannot reference a non pointer")
				p[0].types[0]=p[2].types[0][1:]
				p[0].extra['layerNum']=-1
			else:
				info = findinfo(p[2].idlist[0])
				if (info.type).startswith('arr') and 'AddrList' in p[0].extra:
					p[0].code.append(['=',v,p[0].extra['AddrList'][0]])
				elif 'AddrList' in p[0].extra:
					p[0].code.append(['addr',v,p[0].extra['AddrList'][0]])
				else:
					p[0].code.append(['addr',v,p[2].place[0]])
				p[0].types = ['*' + p[2].types[0]]
				p[0].place=[v]


def p_unary_op(p):
		'''UnaryOp : PLUS
							 | MINUS
							 | MULTIPLY
							 | AND '''
		if p[1] == '+':
				p[0] = ["+"]
		elif p[1] == '-':
				p[0] = ["-"]
		elif p[1] == '*':
				p[0] = ["*"]
		elif p[1] == '&':
				p[0] = ["&"]
# -------------------------------------------------------


# -----------------CONVERSIONS-----------------------------
def p_conversion(p):
		'''Conversion : TYPECAST Type LPAREN Expression RPAREN'''
		p[0] = p[4]
		p[0].types = [p[1].types[0]]
# ---------------------------------------------------------


# ---------------- STATEMENTS -----------------------
def p_statement(p):
	'''Statement : Declaration
							 | LabeledStmt
							 | SimpleStmt
							 | ReturnStmt
							 | BreakStmt
							 | ContinueStmt
							 | GotoStmt
							 | CreateScope IFSYM Block EndScope_1
							 | IfStmt
							 | SwitchStmt
							 | ForStmt
							 | DeferStmt
							 | FallThroughStmt
							 | GoStmt
							 | PrintStmt
							 | ScanStmt'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = p[3]

def p_end_scope_new(p):
  '''EndScope_1 : '''
  # oldScope = curScope
  old_off = scopeDict[curScope].extra['curOffset']
  endscope()
  scopeDict[curScope].extra['curOffset'] = old_off

def p_print_stmt(p):
	'''PrintStmt : PRINT ExpressionList'''
	p[0] = p[2]
	for i in range(len(p[2].types)):
		x =  p[2].types[i]
		if type(p[2].types[i]) is list:
			x = p[2].types[i][0]
		# if x!='int' and x!='cint' and x!='float' and x!='cfloat' and x!='bool' and x!='cbool' and x!='string' and x!='cstring':
		# 	raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't print Expression of unknown type")
		# if p[2]=="%d":
		#   if x!='int' and x!='cint':
		#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Print Expr of type other than int using '%d'")
		if x=='int' or x=='cint' or x=='bool' or x=='cbool' or x.startswith('*'):
			p[0].code.append(['print_int',p[2].place[i]])
		# if p[2]=="%f":
		#   if x!='float' and x!='cfloat':
		#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Print Expr of type other than float using '%f'")
		if x=='float' or x=='cfloat':
			p[0].code.append(['fprint',p[2].place[i]])
		# if p[2]=="%s":
		#   if x!='string' and x!='cstring':
		#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Print Expr of type other than string using '%s'")
		if x=='string' or x=='cstring':
			p[0].code.append(['print_string',p[2].place[i]])

def p_scan_stmt(p):
	'''ScanStmt : SCAN Expression'''
	p[0] = p[2]
	x =  p[2].types[0]
	if type(p[2].types[0]) is list:
		x = p[2].types[0][0]
	if x!='int' and x!='cint' and x!='float' and x!='cfloat' and x!='bool' and x!='cbool' and x!='string' and x!='cstring':
		raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't scan Expression of unknown type")
	# if p[2]=="%d":
	#   if p[3].types[0]!='int' and p[3].types[0]!='cint':
	#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Scan Expr of type other than int using '%d'")
	if x=='int' or x=='cint' or x=='bool' or x=='cbool':
		p[0].code.append(['scan_int',p[2].place[0]])
	# if p[2]=="%f":
	#   if p[3].types[0]!='float' and p[3].types[0]!='cfloat':
	#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Scan Expr of type other than float using '%f'")
	if x=='float' or x=='cfloat':
		p[0].code.append(['fscan',p[2].place[0]])
	# if p[2]=="%s":
	#   if p[3].types[0]!='string' and p[3].types[0]!='cstring':
	#     raise TypeError("Line "+str(p.lineno(1))+" : "+"Can't Scan Expr of type other than string using '%s'")
	if x=='string' or x=='cstring':
		p[0].code.append(['scan_string',p[2].place[0]])

def p_fallthrough_stmt(p):
	'''FallThroughStmt : FALLTHROUGH'''
	p[0] = node()

def p_go_stmt(p):
	'''GoStmt : GO Expression'''
	p[0] = p[2]
	#CHECK


def p_defer_stmt(p):
	'''DeferStmt : DEFER Expression'''
	p[0] = ["DeferStmt","defer",p[2]]


def p_simple_stmt(p):
	''' SimpleStmt : epsilon
								 | ExpressionStmt
								 | IncDecStmt
								 | Assignment
								 | ShortVarDecl '''
	p[0] = p[1]


def p_labeled_statements(p):
	''' LabeledStmt : Label COLON Statement '''
	if checkid(p[1],"label"):
		raise NameError("Line "+str(p.lineno(1))+" : "+"Label "+p[1]+" already exists")
	new1 = ''
	if p[1] in labelDict:
		scopeDict[0].insert(p[1],"label")
		scopeDict[0].updateAttr(p[1],'label',labelDict[p[1]][1])
		labelDict[p[1]][0]=True
		new1 = labelDict[p[1]][1]
	else:
		new1 = newlabel()
		scopeDict[0].insert(p[1],"label")
		scopeDict[0].updateAttr(p[1],'label',new1)
		labelDict[p[1]] = [True,new1]
	p[0] = p[3]
	p[0].code = [['label',new1]] + p[0].code

def p_label(p):
	''' Label : IDENTIFIER '''
	p[0]=p[1]


def p_expression_stmt(p):
	''' ExpressionStmt : Expression '''
	# p[0] = ["ExpressionStmt", p[1]]
	p[0] = node()
	p[0].code = p[1].code

def p_inc_dec(p):
	''' IncDecStmt : Expression INCREMENT
								 | Expression DECREMENT '''
	p[0] = node()
	p[0].code = p[1].code
	p[0].code.append([p[2],p[1].place[0]])


def p_assignment(p):
	''' Assignment : ExpressionList assign_op ExpressionList'''
	if len(p[1].place)!=len(p[3].types):
		raise ValueError("Line "+str(p.lineno(1))+" : "+"No. of expressions on both sides of assignment are not equal")
	p[0] = node()
	p[0].code = p[1].code
	p[0].code+=p[3].code
	for i in range(len(p[1].place)):
		if p[1].types[i]=='float' or p[1].types[i]=='cfloat':
			p[2] = 'f' + p[2]
		if p[2]=='=':
			if not equalcheck(p[1].types[i],p[3].types[i]):
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Types of expressions on both sides of = don't match")
			else:
				if p[1].types[i].startswith('*'):
					if p[3].types[0]=='*NULL':
						c = newconst()
						p[0].code.append(['=',c,'0'])
						p[0].code.append(['=',p[1].place[i],c])
						return
					if p[1].types[i].startswith('*type'):
						scopeDict[curScope].updateExtra(p[1].idlist[i],'*struct')
		else:
			if not opTypeCheck(p[1].types[i],p[3].types[i],p[2][0]):
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Types of expressions on both sides of = don't match")

		if p[1].types[i].startswith('c'):
			raise TypeError("Line "+str(p.lineno(1))+" : "+"Cannot assin to assign_op a const variable ")
		if p[2]=='/=':
			p[0].code.append(['/=',p[1].place[i],p[3].place[i]])
		elif p[2]=='%=':
			p[0].code.append(['%=',p[1].place[i],p[3].place[i]])
		elif p[2]=='*=':
			p[0].code.append(['*=',p[1].place[i],p[3].place[i]])
		else:
			p[0].code.append([p[2],p[1].place[i],p[3].place[i]])

		if p[2]=='<<=' or p[2]=='>>=':
			if p[3].types[i]!='int' and p[3].types[i]!='cint':
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Operand for right/left shift is not integer")

		# if p[1].extra['AddrList'][i]!='None':
		#   p[0].code.append(['store',p[1].extra['AddrList'][i],p[1].place[i]])


def p_assign_op(p):
	''' assign_op : AssignOp'''
	p[0] = p[1]

def p_AssignOp(p):
	''' AssignOp : PLUSEQUAL
							 | MINUSEQUAL
							 | TIMESEQUAL
							 | DIVIDE_EQUAL
							 | MODEQUAL
							 | ANDEQUAL
							 | OREQUAL
							 | XOREQUAL
							 | ANDXOR_EQUAL
							 | LSHIFT_EQUAL
							 | RSHIFT_EQUAL
							 | EQUALS '''
	p[0] = p[1]

# -------------   IF STMT   ------------------------

def p_if_statement(p):
	''' IfStmt : IF Expression CreateScope IFSYM Block EndScope_1 ElseOpt '''
	p[0] = node()
	p[0].code = p[2].code
	if p[2].types[0]!='bool' and p[2].types[0]!='cbool' and p[2].types[0]!='int' and p[2].types[0]!='cint':
		raise TypeError("Line "+str(p.lineno(1))+" : "+"Type of expression is not bool or integer for IF Statement")
		return
	l1 = newlabel()
	l2 = newlabel()
	p[0].code += [['ifgoto',p[2].place[0],l1]]
	p[0].code += p[5].code
	p[0].code += [['goto',l2]]
	p[0].code += [['label',l1]]
	p[0].code += p[7].code
	p[0].code += [['goto',l2]]
	p[0].code += [['label',l2]]

def p_if_sym(p):
	'''IFSYM : '''
	par = scopeDict[curScope].parent
	poff = scopeDict[par].extra['curOffset']
	scopeDict[curScope].updateExtra('curOffset',poff)

def p_else_opt(p):
	''' ElseOpt : ELSE IfStmt
							| ELSE CreateScope IFSYM Block EndScope_1
							| epsilon '''
	if len(p) == 3:
		p[0] = p[2]
	elif len(p)==6:
		p[0] = p[4]
	else:
		p[0]=p[1]

# ------------------- SWITCH STMT ----------------------------


def p_switch_statement(p):
	''' SwitchStmt : ExprSwitchStmt'''
	p[0] = p[1]

def p_ExprSwitchStmt(p):
	'''ExprSwitchStmt : SWITCH Expression CCreateScope LCURL StartSwitch ExprCaseClauseList RCURL EndScope_1'''
	p[0]=p[2]
	dLabel = None
	l1 = newlabel()
	p[0].code += [['goto',l1]]
	
	p[0].code += p[6].code
	p[0].code += [['label',l1]]
	p_6_rep = []
	for i in p[6].extra['exprList']:
		if len(i)!=0:
			p_6_rep.append(i)
	p[0].code += p_6_rep
	
	for i in range(len(p[6].extra['labels'])):
		if p[6].extra['labeltype'][i] == 'default':
			dLabel = p[6].extra['labels'][i]
		else:
			v = newvar()
			v_decl(v,curScope)
			p[0].code += [['!=',v,p[2].place[0],p[6].place[i]]]
			p[0].code += [['ifgoto',v,p[6].extra['labels'][i]]]
	if dLabel is not None:
		p[0].code += [['goto',dLabel]]
	else:
		l = newlabel()
		p[0].code += [['goto',l]]
		p[0].code += [['label',l]]
	p[0].code += [['label',p[5].extra['end']]]

def p_start_switch(p):
	'''StartSwitch : '''
	p[0] = node()
	l2 = newlabel()
	scopeDict[curScope].updateExtra('endofAll',l2)
	p[0].extra['end'] = l2
	par = scopeDict[curScope].parent
	poff = scopeDict[par].extra['curOffset']
	scopeDict[curScope].updateExtra('curOffset',poff)

def findLabel(name):
	for scope in scopeStack[::-1]:
		if name in scopeDict[scope].extra:
			return scopeDict[scope].extra[name]
	raise ValueError("Line "+str(p.lineno(1))+" : "+"Not defined in any loop scope")

def p_ExprCaseClauseList(p):
		'''ExprCaseClauseList : epsilon
								 | ExprCaseClauseList ExprCaseClause
		'''
		if len(p) == 2:
				p[0]=p[1]
				p[0].extra['labels'] = []
				p[0].extra['labeltype'] = []
				p[0].extra['exprList'] = [[]]
		else:
				p[0] = p[1]
				p[0].code += p[2].code
				p[0].place += p[2].place
				p[0].extra['labels'] += p[2].extra['labels']
				p[0].extra['labeltype'] += p[2].extra['labeltype']
				p[0].extra['exprList'] += p[2].extra['exprList']

def p_ExprCaseClause(p):
		'''ExprCaseClause : ExprSwitchCase COLON StatementList '''
		p[0] = node()
		
		if p[1].extra['labeltype'][0]=='default':
			l = newlabel()
			v = [l]
		else:
			l = p[1].extra['labels'][0]
			v =[]
			for i in range(len(p[1].extra['labels'])):
				v.append(p[1].extra['labels'][i])
			
		p[0].code = [['label',l]]
		p[0].code += p[3].code
		p[0].extra['labels'] = v
		lend = findLabel('endofAll')
		
		p[0].code.append(['goto',lend])
		p[0].extra['exprList'] = p[1].extra['exprList']
		p[0].place = p[1].place
		p[0].extra['labeltype'] = p[1].extra['labeltype']

def p_ExprSwitchCase(p):
		'''ExprSwitchCase : CASE ExpressionList
								 | DEFAULT 
		'''
		if len(p) == 3:
				p[0] = p[2]
				# p[0].extra['labeltype'] = ['case']
				p[0].extra['exprList'] = p[2].code
				p[0].extra['labels'] =[]
				p[0].extra['labeltype'] = []
				l = newlabel()
				
				for i in range(len(p[2].place)):
					(p[0].extra['labels']).append(l)
					(p[0].extra['labeltype']).append('case')
		else:
				p[0] = node()
				v = newvar()
				p[0].extra['labeltype'] = ['default']
				p[0].extra['exprList'] = [[]]
				p[0].extra['place'] = [v]


# --------- FOR STMT   -------------------------------

def p_for(p):
	'''ForStmt : FOR CCreateScope ConditionBlockOpt Block EndScope_1'''
	p[0] = node()
	l1 = p[3].extra['before']
	p[0].code = p[3].code + p[4].code
	if 'incr' in p[3].extra:
		p[0].code += p[3].extra['incr']
	p[0].code += [['goto',l1]]
	l2 = p[3].extra['after']
	p[0].code += [['label',l2]]

def p_c_create_scope(p):
	'''CCreateScope : '''
	x = scopeDict[curScope].extra['curOffset']
	addscope(None,x)

def p_conditionblockopt(p):
	'''ConditionBlockOpt : epsilon
						 | Condition
						 | ForClause'''
	p[0] = p[1]
	# l1 = newlabel()
	# p[0].code += [['label',l1]]
	# p[0].extra['before'] = l1
	
	# par = scopeDict[curScope].parent
	# poff = scopeDict[par].extra['curOffset']
	# scopeDict[curScope].updateExtra('curOffset',poff)

def p_condition(p):
	'''Condition : Expression '''
	p[0]=p[1]
	

def p_forclause(p):
	'''ForClause : SimpleStmt Semi ConditionOpt Semi SimpleStmt'''
	p[0] = p[1]
	l1 = newlabel()
	p[0].code += [['label',l1]]
	p[0].extra['before'] = l1
	p[0].code += p[3].code
	p[0].extra['before'] = l1
	l2 = newlabel()
	scopeDict[curScope].updateExtra('beginFor',l1)
	scopeDict[curScope].updateExtra('endFor',l2)
	p[0].extra['after'] = l2
	if len(p[3].place)!=0:
		p[0].code += [['ifgoto',p[3].place[0],l2]]
	p[0].extra['incr'] = p[5].code


def p_conditionopt(p):
	'''ConditionOpt : epsilon
					| Condition '''
	p[0] = p[1]


# ----------------- RETURN STMT  --------------------------

def p_return(p):
	'''ReturnStmt : RETURN ExpressionListPureOpt'''
	p[0] = p[2]

	for scope in scopeStack[::-1]:
		if 'fName' in scopeDict[scope].extra:
			fname = scopeDict[scope].extra['fName']
			retType = scopeDict[scope].extra['retType']
			return_off = scopeDict[scope].extra['parOffset']
	funcinfo = findinfo(fname)
	l = funcinfo.retsize
	# 1 return value
	if len(p[2].types) == 1:
		if not equalcheck(retType,p[2].types[0]):
			raise TypeError("Line "+str(p.lineno(1))+" : "+"Function "+fname+" has return type "+retType+" which doesnt match that in stmt i.e. "+p[2].types[0] )
		s = p[2].place[0]
		p[0].code.append(['push',s,str(l[0]),str(return_off)])

	# void return
	elif len(p[2].types) == 0:
		if retType!='void':
			raise TypeError("Line "+str(p.lineno(1))+" : "+"function "+fname+" has return type "+retType+" , but returned void in the stmt")
	# Multiple return
	else:
		if len(p[2].types)!=len(retType):
			raise TypeError("Line "+str(p.lineno(1))+" : "+"Number of return argument doesn't match for "+fname)
		leng = len(p[2].place)
		for i in range(len(p[2].place)):
			if not equalcheck(retType[i],p[2].types[i]):
				raise TypeError("Line "+str(p.lineno(1))+" : "+"Function "+fname+" has return type "+retType[i]+" which doesnt match that in stmt i.e. "+p[2].types[i] )
			s = p[2].place[leng-i-1]
			k = l[leng-i-1]
			x = return_off
			p[0].code.append(['push',s,str(k),str(x)])
			return_off += funcinfo.retsize[leng-i-1]
	jumpval = funcinfo.mysize + 4
	p[0].code.append(['jret','$ra',fname])

def p_expressionlist_pure_opt(p):
	'''ExpressionListPureOpt : ExpressionList
						 | epsilon'''
	p[0] = p[1]
	

def p_break(p):
	'''BreakStmt : BREAK LabelOpt'''
	p[0] = ["BreakStmt", "break", p[2]]

def p_continue(p):
	'''ContinueStmt : CONTINUE LabelOpt'''
	p[0] = ["ContinueStmt", "continue", p[2]]

def p_labelopt(p):
	'''LabelOpt : Label
				| epsilon '''
	# p[0] = ["LabelOpt", p[1]]
	p[0] = p[1]

def p_goto(p):
	'''GotoStmt : GOTO Label '''
	p[0] = ["GotoStmt", "goto", p[2]]


# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
		'''SourceFile : PackageClause Semi ImportDeclRep TopLevelDeclRep'''
		p[0] = p[1]
		p[0].code+=p[3].code
		p[0].code+=p[4].code
		p[0].idlist += p[3].idlist
		p[0].idlist += p[4].idlist

def p_import_decl_rep(p):
	'''ImportDeclRep : epsilon
					 | ImportDeclRep ImportDecl Semi'''
	if len(p) == 4:
		p[0] = p[1]
		p[0].code +=p[2].code
		p[0].idlist += p[2].idlist
	else:
		p[0] = p[1]

def p_toplevel_decl_rep(p):
	'''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl Semi
										 | epsilon'''
	if len(p) == 4:
		p[0] = p[1]
		p[0].code+=p[2].code
		p[0].idlist += p[2].idlist
	else:
		p[0] = p[1]


# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
		'''PackageClause : PACKAGE PackageName'''
		p[0] = p[2]


def p_package_name(p):
		'''PackageName : IDENTIFIER'''
		p[0]=node()
		p[0].idlist.append(str(p[1]))
		if checkid(p[1],'e'):
			raise NameError("Line "+str(p.lineno(1))+" : "+"Package Name"+p[1]+"already exists")
		# else:
			# scopeDict[0].insert(p[1],"package")


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
	'''ImportDecl : IMPORT ImportSpec
					| IMPORT LPAREN ImportSpecRep RPAREN '''
	if len(p) == 3:
		p[0] = p[2]
	else:
		p[0] = p[3]

def p_import_spec_rep(p):
	''' ImportSpecRep : ImportSpecRep ImportSpec Semi
						| epsilon '''
	if len(p) == 4:
		p[0] = p[1]
		p[0].idlist+=p[2].idlist
	else:
		p[0] = p[1]

def p_import_spec(p):
	''' ImportSpec : PackageNameDotOpt ImportPath '''
	p[0]=p[1]
	if len(p[1].idlist)!=0:
		p[0].idlist = p[1].idlist + " " + p[2].idlist
	else:
		p[0].idlist+=p[2].idlist

def p_package_name_dot_opt(p):
	''' PackageNameDotOpt : DOT
												| PackageName
												| epsilon'''
	if p[1]== '.':
		p[0] = node()
		p[0].idlist.append('.')
	else:
		p[0] = p[1]

def p_import_path(p):
	''' ImportPath : STRING_LIT '''
	p[0]=node()
	p[0].idlist.append(str(p[1]).replace('\"',''))
	scopeDict[0].insert(str(p[1]).replace('\"',''),"import")
	
# ----------------- Semicolon  --------------------

def p_SemiColon(p):
	'''Semi : SEMICOLON'''
	p[0] = ";"
	# global constNum
	# constNum = 0

# def p_identifier(p):
#   '''Identifier : IDENTIFIER'''
#   p[0] = newvar()
#   v_decl(p[0],curScope)

# ---------------   EMPTY and SYNTAX ERROR --------------

def p_empty(p):
	'''epsilon : '''
	p[0] = node()


def p_error(p):
		if p:
			print("Syntax error at line no:", str(p.lineno), "at position", p.lexpos, "in the code.   " "TOKEN VALUE=", p.value,  "TOKEN TYPE=" ,p.type)
			parser.errok()
		else:
			print("Syntax error at EOF")

parser = yacc.yacc()


with open(file_name,'r') as f:
		input_str = f.read()
result=parser.parse(input_str,tracking=True)



def print_in_format():
	tab = [[]]
	tab[0] = ['Scope,','Name,','Type,','CName','Offset,','Child']
	for i in range(len(scopeDict)):
		symtab = scopeDict[i]
		for j in symtab.symbols:
			s = ""
			t = symtab.table[j].type
			if type(t) is list:
				for k in t:
					if k[:4]=="type":
						k = 'struct'
					if k[:5]=='*type':
						k='*struct'
					s += str(k)+"_"
				s = s[:-1]
			else:
				k = t
				if not t:
					t=""
					k=""
				# if k[:4]=="type":
				# 	k = 'struct'
				# if k[:5]=='*type':
				# 	k='*struct'
				s = k
			scope = str(i)
			name = j
			typ = s
			lab = str(symtab.table[j].place)
			off = str(symtab.table[j].offset)
			if symtab.table[j].child:
				child = str(symtab.table[j].child.val)
			else:
				child = ""
			tab.append([scope+',',name+',',typ+',',lab+',',off+',',child])
		# info = scopeDict[i].retrieve()
	col_width = max(len(word) for row in tab for word in row) + 1
	flag = 0
	for row in tab:
		print "".join(word.ljust(col_width) for word in row)

# csv_name = file_name[:-3]

sys.stdout =  open("Table.csv", "w+")
print_in_format()

# info1 = findinfo('i',2)


def print_3AC(l):
	for i in l:
		s = ""
		for j in i:
			s+=str(j)+" "
		print s


sys.stdout =  open("3AC.txt", "w+")
print_3AC(result.code)

Symbol_Table = scopeDict
Code = result.code

sys.stdout = sys.__stdout__


# print_list(result.code)


# info2 = findinfo('age',2)
