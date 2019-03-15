#!/usr/bin/env python2
import ply.yacc as yacc
import sys
import os
from lexer import *
from symbol import *
# from scope import *

root = None

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
  return False

def checkid(name,str):
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
    # print "---------------------->"+name
    if scopeDict[curScope].retrieve(name) is not None:
      return True
    return False

  return False

def opTypeCheck(a,b,op):
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
arrNum = 0
labelNum = 1
constNum = 0
mainFunc = True

labelDict = {}
scopeDict = {}
scopeDict[0] = st(0)
scopeDict[0].updateExtra('curOffset',0)
scopeStack=[0]

def addscope(name=None):
  # print name
  global scopeLevel
  global curScope
  scopeLevel+=1
  scopeStack.append(scopeLevel)
  scopeDict[scopeLevel] = st(scopeLevel)
  scopeDict[scopeLevel].setParent(curScope)
  scopeDict[scopeLevel].updateExtra('curOffset',0)
  # if mainFunc:
  #   y = scopeDict[0].extra['curOffset']
  #   scopeDict[scopeLevel].updateExtra('curOffset',y)
  if name is not None:
    # Not sure if correct
    # print name
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
  # print "Inside EndScope:"
  # print curScope
  # print scopeStack
  curScope = scopeStack.pop()
  # print curScope
  curScope = scopeStack[-1]
  # print curScope

def findscope(name):
  for s in scopeStack[::-1]:
    if scopeDict[s].retrieve(name) is not None:
      return s

  raise NameError(name+ "is not defined in any scope")

def findinfo(name, S=-1):
  # print S
  if S > -1:
    # print S
    if scopeDict[S].retrieve(name) is not None:
        return scopeDict[S].retrieve(name)
    raise NameError("Identifier " + name + " is not defined!")

  for scope in scopeStack[::-1]:
    if scopeDict[scope].retrieve(name) is not None:
        info = scopeDict[scope].retrieve(name)
        return info

  raise NameError("Identifier " + name + " is not defined!")


# -------------  SOME OTHER FUNCTIONS ---------------------


def newvar():
  global varNum
  val = 'v'+str(varNum)
  varNum+=1
  return val

def newconst():
  global constNum
  val = 'temp_c'+str(constNum)
  constNum+=1
  return val

def newlabel():
  global labelNum
  val = 'l'+str(labelNum)
  labelNum+=1
  return val

def newarray():
  global arrNum
  val = 'arr'+str(arrNum)
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
    # print p[0].__dict__


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
  # print "here ==========> "+name
  # print scopeStack
  for scope in scopeStack[::-1]:
    # print scopeDict[scope].table
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
          p[0].bytesize = 1
        else:
          p[0].size = [8]
          p[0].bytesize = 8
          # maximum size of string set to 8 bytes
    else:
        if not definedcheck(p[2]):
          raise TypeError("TypeName " + p[2] + " not defined anywhere")
        else:
          p[0]=node()
          var = findinfo(p[2],0)
          p[0].types.append(var.type)
          # print "TypeToken"
          # print var.type
          # print var.mysize
          p[0].size = [var.mysize]
          # print var.__dict__
          #TODO
          # coff = scopeDict[curScope].extra['curOffset']
          # print p[-1].idlist[0]
          p[0].bytesize = var.mysize
          # print coff
          # print var.mysize
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
  # print "ST"
  # print curScope
  # print scopeDict[curScope].extra['structname']

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
    raise IndexError("Index of array "+p[-1].idlist[0]+" is not integer")
  x = p[2].extra['operandValue'][0]
  p[0].bytesize *= int(x)
  if p[4].types[0]=='arr':
    p[0].types = ['arr'] + p[4].types
    if 'operandValue' in p[2].extra:
      p[0].limits = p[2].extra['operandValue']
      p[0].limits += p[4].limits
    a = p[4].size[0][:4]
  else:
    p[0].types = ['arr'] + p[4].types
    if 'operandValue' in p[2].extra:
      p[0].limits = p[2].extra['operandValue']
    a = newarray()

  # print "Print code in ArrayType:"
  
  a += '_'+str(len(p[0].limits))
  p[0].code.append(['=',a,p[2].place[0]])
  # print print_list(p[0].code)
  # print "ArrayType:"
  # print p[4].size
  p[0].size = [a] + p[4].size


def p_array_length(p):
  ''' ArrayLength : Expression '''
  p[0]=p[1]

def p_element_type(p):
  ''' ElementType : Type '''
  p[0]=p[1]

# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
  '''StructType : FuncScope STRUCT LCURL FieldDeclRep RCURL EndScope'''
  p[0] = p[4]
  info = findinfo(p[-1],0)
  # print "StructType:"
  # print p[-1]
  # print p[4].bytesize
  # print p[-1]
  p[0].types = [info.type]
  scopeDict[curScope].updateAttr(p[-1],'mysize',p[4].bytesize)
  p[0].bytesize = p[4].bytesize
  
  # print p[0].__dict__

def p_func_scope(p):
  '''FuncScope : '''
  p[0] = node()
  # scopeDict[curScope].updateExtra('structPscope',curScope)
  x = curScope
  # print x
  addscope(p[-1])
  scopeDict[curScope].updateExtra('structPscope',x)



def p_field_decl_rep(p):
  ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
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
  # print "Struct:"
  # print p[2].bytesize
  
  # print p[2].types
  sco = scopeDict[curScope].extra['structPscope']
  s = scopeDict[sco].extra['structname']
  # print s
  if s in p[2].types:
    raise TypeError("Struct "+s[4:]+" recursively defind, not allowed")
  # if x in p[2].types
  for i in range(len(p[0].idlist)):
    p[0].bytesize += p[2].bytesize
    x = p[0].idlist[i]
    # print p[1].idlist[i]
    # print p[2].size[0]
    info = findinfo(x)
    scopeDict[curScope].updateAttr(x,'type',p[2].types[0])
    y = scopeDict[curScope].extra['curOffset']
    info.offset = y
    scopeDict[curScope].extra['curOffset'] += p[2].bytesize
    # print y
    info.mysize = p[2].bytesize
    # print x
    # print info.mysize
    # print y
    # print p[2].size
    # scopeDict[curScope].updateExtra('curOffset',y+p[2].size[0])
    # p[0].bytesize +=p[2].size[0]
    # print scopeDict[curScope].extra['curOffset']


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MULTIPLY BaseType'''
    p[0] = p[2]
    p[0].size = ['inf']+p[0].size
    p[0].types[0]="*"+p[0].types[0]
    p[0].bytesize = 4
    # print p[0].types

def p_base_type(p):
    '''BaseType : Type'''
    p[0]=p[1]
# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
    '''Signature : Parameters ResultOpt'''
    p[0]=p[1]
    scopeDict[curScope].updateExtra('types',p[1].types)
    scopeDict[0].insert(p[-2],'sigType')
    if len(p[2].types)==0:
      scopeDict[0].updateAttr(p[-2],'ret','void')
    else:
      for i in range(len(p[2].types)):
        scopeDict[0].updateAttr(p[-2],'ret',p[2].types[i])
    p[0].extra['fName'] = p[-2]
    info = findinfo(p[-2],0)
    if info.label==None:
      lnew = newlabel()
      scopeDict[0].updateAttr(p[-2],'label',lnew)
      scopeDict[0].updateAttr(p[-2],'child',scopeDict[curScope])
    p[0].types = p[2].types

def p_result_opt(p):
    '''ResultOpt : Result
                 | epsilon'''
    p[0]=p[1]

def p_result(p):
    '''Result : Parameters
              | Type'''
    p[0]=p[1]


def p_params(p):
    '''Parameters : LPAREN ParametersList RPAREN
                  | LPAREN RPAREN'''
    if len(p) == 4:
      p[0] = p[2]
      # print "Parameters:"
      # print p[0].idlist
      # print p[0].types
      scopeDict[curScope].updateExtra('parOffset',0)
      l = len(p[0].idlist)-1
      for i in range(len(p[0].idlist)):
        ind = l-i
        # print "->"
        x = p[0].idlist[ind]
        info = findinfo(x)
        y = scopeDict[curScope].extra['parOffset']
        z = info.mysize
        scopeDict[curScope].extra['parOffset'] -= z
        info.offset = scopeDict[curScope].extra['parOffset']

    else:
      p[0] = node()

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

def p_param_decl(p):
    '''ParameterDecl : IdentifierList Type
                     | Type'''
    p[0] = p[1]
    if len(p) == 3:
      for x in p[1].idlist:
        scopeDict[curScope].updateAttr(x,'type',p[2].types[0])
        p[0].types.append(p[2].types[0])
        # print "=>"
        # print p[2].bytesize
        info = findinfo(x)
        info.mysize = p[2].bytesize
        # if pointer
        if (p[2].types[0]).startswith('*'):
          t = p[2].types[0]
          for i in range(len(t)):
            if t[i]!='*':
              break
          if t[i:] == 'int' or t[i:]=='float':
            scopeDict[curScope].updateAttr(x,'size',['inf',4])
          #TODO if time permits: typedef pointers


#-----------------------BLOCKS---------------------------
def p_block(p):
    '''Block : LCURL StatementList RCURL'''
    p[0] = p[2]

def p_stat_list(p):
    '''StatementList : StatementRep'''
    p[0] = p[1]

def p_stat_rep(p):
    '''StatementRep : StatementRep Statement SEMICOLON
                    | epsilon'''
    if len(p) == 4:
        p[0] = p[1]
        p[0].code += p[2].code
        # print p[0].__dict__
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
    '''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
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
      raise ValueError("Error: Unequal number of identifiers and Expressions")
    for i in range(len(p[1].place)):
      x = p[1].idlist[i]
      info = findinfo(x)
      p[1].place[i] = p[2].place[i]
      p[0].bytesize += p[2].bytesize
      info.mysize = p[2].bytesize
      info.offset = scopeDict[curScope].extra['curOffset']
      # print info.offset
      scopeDict[curScope].extra['curOffset'] += p[2].bytesize
      scope = findscope(x)
      scopeDict[scope].updateAttr(x,'place',p[1].place[i])
      if p[2].types[i]==i:
        raise TypeError('Type of ' + p[0].idlist[i] + 'does not match that of expr')
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
      p[0].idlist+=[p[1]]
      if checkid(p[1],"e"):
        raise NameError(p[1]+" : This name already exists")
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
        raise NameError(p[3]+" : This name already exists")
      else:
        scopeDict[curScope].insert(p[3],None)
        v = newvar()
        p[0].place = p[0].place + [v]
        scopeDict[curScope].updateAttr(p[3],'place',v)
    else:
      p[0]=node()
      p[0].idlist = [p[1]] + [p[3]]
      if checkid(p[1],"e") or checkid(p[3],"e"):
        if checkid(p[1],"e"):
          raise NameError(p[1]+" : This name already exists")
        else:
          raise NameError(p[3]+" : This name already exists")
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
    p[0]=p[2]
    p[0].code = p[1].code+p[0].code
    p[0].place = p[1].place + p[0].place
    p[0].types = p[1].types + p[0].types
    p[0].idlist = p[1].idlist + p[0].idlist
    if 'AddrList' not in p[1].extra:
      p[1].extra['AddrList'] = ['None']
    p[0].extra['AddrList'] += p[1].extra['AddrList']

def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                     | epsilon'''
    if len(p) == 4:
        p[0]=p[1]
        p[0].code+=p[3].code
        p[0].types+=p[3].types
        p[0].place+=p[3].place
        p[0].idlist += p[3].idlist
        if 'AddrList' not in p[3].extra:
          p[3].extra['AddrList'] = ['None']
        p[0].extra['AddrList'] += p[3].extra['AddrList']
    else:
        p[0]=p[1]
        p[0].extra['AddrList'] = []
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
    '''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
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
      raise NameError("Name "+p[1]+" already defined")
    else:
      # print p[1] + "  " + str(curScope)
      scopeDict[curScope].insert(p[1],p[3].types[0])
    p[0]=node()
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENTIFIER Type'''
    if checkid(p[1],'andsand'):
      raise NameError("Name "+p[1]+" already defined")
    else:
      # print p[1]
      # print p[2].types
      scopeDict[curScope].insert(p[1],p[2].types[0])
    p[0]=node()
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
    '''VarDecl : VAR VarSpec
               | VAR LPAREN VarSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = p[2]
        # print p[0].bytesize
    else:
        p[0] = p[3]

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                  | epsilon'''
    if len(p) == 4:
        p[0] = p[1]
        p[0].code+=p[2].code
        p[0].bytesize += p[2].bytesize
        # print p[0].bytesize
    else:
        p[0]=p[1]

def p_var_spec(p):
  '''VarSpec : IdentifierList Type ExpressionListOpt'''
  if len(p[3].place)==0:
    p[0]=p[1]
    p[0].code+=p[2].code
    # p[0].bytesize = p[2].bytesize
    # print "VarSpec : "
    # print p[1].idlist
    if p[2].types[0]=='arr':
      v = p[2].size[0]
      for i in range(len(v)):
        if v[i]=='_':
          break
      v = v[:i+1] + 'size'
      # print v
      p[0].code.append(['=',v,1])
      # print p[2].size
      for i in p[2].size:
        if p[2].size[0]!='inf':
          p[0].code.append(['x=',v,i])
    # print print_list(p[0].code)
    for i in range(len(p[1].idlist)):
      x = p[1].idlist[i]
      s = findscope(x)
      # print x
      # print p[2].types
      info = findinfo(x)
      
      #For arrays
      if p[2].types[0] == 'arr':
        scopeDict[curScope].updateExtra(x,p[2].limits)
        scopeDict[s].updateAttr(x,'type',p[2].types)
        p[0].code.append(['array',x,v])
        # print print_list(p[0].code)
        # print p[2].size
        scopeDict[s].updateAttr(p[1].idlist[i],'size',p[2].size)
        p[0].bytesize += p[2].bytesize
        info.mysize = p[2].bytesize
        info.offset = scopeDict[curScope].extra['curOffset']
        # print info.offset
        scopeDict[curScope].extra['curOffset'] += p[2].bytesize
        # print scopeDict[curScope].extra['curOffset']
        # print p[2].bytesize
      else:
        scopeDict[s].updateAttr(x,'type',p[2].types[0])
        p[0].bytesize += p[2].bytesize
        # print p[0].bytesize
        info.mysize = p[2].bytesize
        info.offset = scopeDict[curScope].extra['curOffset']
        scopeDict[curScope].extra['curOffset'] += p[2].bytesize
        # p[0].code.append(['=',x,p[1].place[i]])
        # print x
        # print scopeDict[curScope].extra['curOffset']
    return
  p[0]=node()
  p[0].code = p[1].code + p[3].code
  if len(p[1].place)!=len(p[3].place):
    raise ValueError("Mismatch in number of expressions assigned to variables")

  # print "VarSpec:"
  for i in range(len(p[1].place)):
    x = p[1].idlist[i]
    # print x
    # print p[3].place[i]
    p[1].place[i] = x
    scope = findscope(x)
    info = findinfo(x)
    p[0].code.append(['=',x,p[3].place[i]])
    scopeDict[scope].updateAttr(x,'place',p[1].place[i])
    scopeDict[scope].updateAttr(x,'type',p[2].types[0])
    p[0].bytesize += p[2].bytesize
    info.offset = scopeDict[curScope].extra['curOffset']
    info.mysize = p[2].bytesize
    scopeDict[curScope].extra['curOffset'] += p[2].bytesize
    #pointer case
    if p[2].types[0][0]=='*':
      scopeDict[scope].updateAttr(x,'size',p[2].size)
    if type(p[3].types[i]) is list:
      s = p[3].types[i][0]
    else:
      s = p[3].types[i]
    # print s + "  ->  "+ x
    if not equalcheck(p[2].types[0],s):
      raise TypeError("Type of "+ x + " does not match that of expr")


def p_expr_list_opt(p):
    '''ExpressionListOpt : EQUALS ExpressionList
                         | epsilon'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0]=p[1]
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECL-------------
def p_short_var_decl(p):
  ''' ShortVarDecl : IDENTIFIER SHORT_ASSIGNMENT Expression '''
  p[0] = node()
  if checkid(p[1],'e'):
    raise NameError("Variable"+p[1]+"already exists.")
  else:
    scopeDict[curScope].insert(p[1],None)
  v = newvar()
  p[0].code = p[3].code
  # print "ShortVarDecl:"
  # print p[1]
  # print p[3].place
  p[0].code.append(['=',p[1],p[3].place[0]])
  # print print_list(p[0].code)
  x = p[3].types[0]
  if x=='int' or x=='cint':
    p[0].bytesize = 4
  info = findinfo(p[1])
  info.offset = scopeDict[curScope].extra['curOffset']
  info.mysize = p[0].bytesize
  scopeDict[curScope].extra['curOffset'] += p[0].bytesize
  scopeDict[curScope].updateAttr(p[1],'place',p[1])
  scopeDict[curScope].updateAttr(p[1],'type',p[3].types[0])



# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
  '''FunctionDecl : FUNC FunctionName CreateScope Function EndScope
                  | FUNC FunctionName CreateScope Signature EndScope'''
  p[0]=node()
  # print "FunctionDecl: "+p[2]
  # print curScope
  # print scopeDict[curScope].extra['curOffset']
  if len(p[4].code):
    global mainFunc
    if mainFunc:
      mainFunc = False
      p[0].code = [["goto","main"]]
    p[0].code.append(['label',p[2]])
    p[0].code += p[4].code
    # print p[4].__dict__
    # print print_list(p[0].code)
  p[0].idlist += [p[2]]

def p_create_scope(p):
  '''CreateScope : '''
  addscope()
  # print curScope

def p_end_scope(p):
  '''EndScope : '''
  endscope()

def p_func_name(p):
  '''FunctionName : IDENTIFIER'''
  p[0] = p[1]
  # print p[1]

def checksignature(name):
  for scope in scopeStack[::-1]:
    # print scopeDict[scope].table
    if scopeDict[scope].retrieve(name) is not None:
      info = scopeDict[scope].retrieve(name)
      # print name+" ---------> "+info.type
      if info.type=="sigType":
        return True
  return False

def p_func(p):
    '''Function : Signature RetTypeSet FunctionBody'''
    p[0] = p[3]
    # print "Function: "
    # print curScope
    scopeDict[curScope].updateExtra('curOffset',0)
    # print p[3].__dict__
    for i in range(len(p[1].idlist)):
      x = p[1].idlist[i]
      info = findinfo(x)
      # print info.offset
      # load the arguments from the stack
      # left out in this assignment
      # print print_list(p[0].code)
    if checksignature(p[-2]):
      if p[-2]=="main":
        scopeDict[0].updateAttr('main','label','main')
        scopeDict[0].updateAttr('main','child',scopeDict[curScope])
      info = findinfo(p[-2])
      info.type = 'func'
    else:
      raise NameError('No Signature found for '+p[-2])


def p_ret_type_set(p):
  '''RetTypeSet : '''
  fname = p[-1].extra['fName']
  scopeDict[curScope].updateExtra('fName',fname)
  if len(p[-1].types)==1:
    # print p[-1].types
    scopeDict[curScope].updateExtra('retType',p[-1].types[0])
  elif len(p[-1].types)>1:
    scopeDict[curScope].updateExtra('retType',p[-1].types)
  else:
    scopeDict[curScope].updateExtra('retType','void')

def p_func_body(p):
    '''FunctionBody : Block'''
    p[0] = p[1]
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


def p_basic_lit(p):
  '''BasicLit : I INT_LIT
              | F FLOAT_LIT
              | C IMAGINARY_LIT
              | S STRING_LIT'''
  p[0]=node()
  # print "BasicLit : "
  # print p[2]
  c = newconst()
  p[0].code.append(["=",c,p[2]])
  # print_list(p[0].code)
  p[0].place.append(c)
  p[0].extra['operandValue'] = [p[2]]
  p[0].types.append('c'+p[1])

def p_I(p):
  '''I : '''
  p[0] = 'int'

def p_F(p):
  '''F : '''
  p[0] = 'float'

def p_C(p):
  '''C : '''
  p[0] = 'complex'

def p_S(p):
  '''S : '''
  p[0] = 'string'

def p_operand_name(p):
  '''OperandName : IDENTIFIER'''
  if not definedcheck(p[1]):
    raise NameError("identifier " + p[1] + " is not defined")
  p[0] = node()
  info = findinfo(p[1])
  # print "OperandName"
  # print p[1]
  # print info.offset
  # print info.type
  if type(info.type) is list:
    s = info.type[0]
  else:
    s = info.type
  if s=='func' or s=='sigType':
    p[0].types = [info.retType]
    p[0].place.append(info.label)
  else:
    # print p[1]
    # print info.type
    # print info.listsize
    # print info.type
    # if type(info.type) is list:
    #   p[0].types = info.type
    # else:
    p[0].types = [s]
    # print p[0].types
    # print info.place
    off = 'off_'+str(info.offset)
    p[0].place.append(off)
    p[0].extra['layerNum'] = 0
    p[0].extra['operand'] = p[1]
    if info.listsize is not None:
      p[0].size = info.listsize
    else:
      for i in range(len(s)):
        if s[i]!='*':
          break;
      if s[i:]=='int':
        # print "ohh okay"
        p[0].size = ['inf','4']
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
      raise NameError("package"+p[1]+"not included")
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
  # Arrays:
  elif p[2]=='[':
    p[0] = p[1]
    p[0].code+=p[3].code
    name = p[1].extra['operand']
    info = findinfo(p[1].extra['operand'])
    lsize = info.listsize
    if p[3].types[0]!='int' and p[3].types[0]!='cint':
      raise IndexError("Array index of array " + p[1].extra['operand'] + " is not integer")
    k = p[1].extra['layerNum']
    # print "PrimaryExpr(Array) : "+name + ", layer = "+ str(k)
    # print lsize
    # check on index range
    if p[1].extra['layerNum'] == len(lsize)-1:
      raise IndexError('Dimension of array '+p[1].extra['operand'] + ' doesnt match')

    if 'operandValue' in p[3].extra:
      z = p[3].extra['operandValue'][0]
      y = scopeDict[curScope].extra[p[1].extra['operand']]
      if z>=y[k]:
        raise IndexError("Array "+ p[1].extra['operand'] +" out of Bounds "+" at level = "+str(k))
    
    v1 = newvar()
    p[0].code.append(['=',v1,p[3].place[0]])
    for i in lsize[p[1].extra['layerNum']+1:]:
      p[0].code.append(['x=',v1,i])
    # ----------------------------------------------
    v2 = newvar()
    # print p[0].place
    p[0].code.append(['+',v2,p[0].place[0],v1])
    p[0].place = [v2]
    if p[1].extra['layerNum'] == len(lsize)-2:
      v3 = newvar()
      p[0].code.append(['load',v3,v2])
      p[0].place = [v3]
    p[0].extra['AddrList'] = [v2]
    if k==0:
      p[0].types = info.type[1:]
    else:
      p[0].types = p[1].types[1:]
    # print p[0].types
    p[0].extra['layerNum'] += 1
    # print_list(p[0].code)
  # -------------------function case ------------------------
  elif p[2]=='(':
    p[0]=p[1]
    p[0].code+=p[3].code

    listval = []

    for key,value in enumerate(scopeDict[curScope].table):
      cur = findinfo(value,curScope)
      listval.append(value)
      # p[0].code.append(['push',cur.place])

    # print "Function in PrimaryExpr"
    x = p[1].idlist[0]
    # print x

    info = findinfo(p[1].idlist[0],0)
    # print info.__dict__
    functionDict = info.child
    # print "---"
    if len(functionDict.extra['types'])!=len(p[3].place):
      raise IndexError("Function "+x+" passed with Unequal number of arguments")
    paramTypes = functionDict.extra['types']
    if len(p[3].place):
      for x in p[3].place:
        p[0].code.append(['push',x])
      for i in range(len(p[3].place)):
        if not equalcheck(paramTypes[i],p[3].types[i]):
          raise TypeError("Type Mismatch in "+p[1].idlist[0])

    # Checking Return Type
    # print "PrimaryExpr (Function):"
    name = p[1].idlist[0]
    info.label = name
    # print p[0].place
    if len(info.retType)==1:
      v1 = 'temp_'+name+'_1'
      if info.retType[0]=='void':
        p[0].code.append(['call_void',info.label])
      elif info.retType[0]=='int':
        p[0].place = [v1]
        p[0].code.append(['call_int',v1,info.label])
      elif info.retType[0]=='float':
        p[0].place = [v1]
        p[0].code.append(['call_float',v1,info.label])
      elif info.retType[0]=='string':
        p[0].place = [v1]
        p[0].code.append(['call_string',v1,info.label])
      p[0].types = [p[1].types[0]]
      # print p[0].place
    else:
      # print info.retType
      p[0].place = []
      p[0].types = info.retType
      r = []
      k = 1
      for i in range(len(info.retType)):
        s = 'temp_' + name+'_'+str(i+1)
        r.append(s)
        p[0].place.append(s)
      # print p[0].place
      a = ['call_mult'] + r + [info.label]
      p[0].code.append(a)

    # check if needed or not
    var1 = newvar()
    if len(p[3].place):
      for x in p[3].place:
        p[0].code.append(['pop',var1])

    for val in listval[::-1]:
      # print val
      cur = findinfo(val,curScope)
      # p[0].code.append(['pop',cur.place])


  #RESUME
  # ------------------   SELECTOR  -------------------------
  elif len(p) == 4:
    p[0] = p[1]
    # print "Selector:"
    x = p[1].idlist[0]
    # print p[1].idlist
    # print p[2][1]
    # print p[1].idlist
    # print scopeStack
    info = findinfo(x)
    # print info.mysize
    # print info.offset
    # print info.__dict__
    t = info.type
    # print "t = "+t
    if t[0] =='arr':
      for i in range(len(t)):
        if t[i]!='arr':
          break
      t = t[i:][0][4:]
    elif t[0]=='*':
      # print t[1:5]
      if t[1:5]!='type':
        raise TypeError(t+" does not have any attribute")
        return
      if x not in scopeDict[curScope].extra:
        # print "coooooooooooooooooool"
        raise NameError(x+" is not set")
      t = t[5:]
    else:
      t = t[4:]
    # print t
    sinfo = findinfo(t)
    sScope = sinfo.child
    # print sScope.__dict__
    if p[3] not in sScope.table:
      raise NameError("identifier " + p[3]+ " is not defined inside the struct " + x)
    varname = x+'.'+p[3]
    if not checkid(x,'e'):
      raise NameError(x+" does not exist")
    # print varname
    if checkid(varname,'e'):
      # print "Inside check -----------> "+varname
      info1 = findinfo(varname)
      # print info.type
      p[0].place = [info1.place]
      p[0].types = [info1.type]
    else:
      varinfo = sScope.retrieve(p[3])
      # print "varinfo.type = "+varinfo.type
      # print "varinfo.offset = "+str(varinfo.offset)
      # print info.offset
      curoff = info.offset + varinfo.offset
      v = 'off_'+str(curoff)
      p[0].types = [varinfo.type]
      p[0].place = [v]
      scopeDict[curScope].insert(varname,p[0].types[0])
      scopeDict[curScope].updateAttr(varname,'place',v)
      scopeDict[curScope].updateAttr(varname,'offset',curoff)
      # scopeDict[curScope].updateExtra(varname,'defined',False)
    p[0].idlist = [varname]
    # print info.offset
    # p[0] = p[1]
  else:
    # print p[2].__dict__
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
      p[0].code = p[1].code + p[3].code
      p[0].idlist = p[1].idlist + p[3].idlist
      if p[2]=='<<' or p[2]=='>>'and p[3].types[0]!='int' and p[3].types[0]!='cint':
          raise TypeError("RHS of shift operator is not integer")
      if not opTypeCheck(p[1].types[0],p[3].types[0],'.'):
        # print p[2] + p[1].types[0] + p[3].types[0]
        if (p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/') and (p[1].types[0]=='cint'or p[1].types[0]=='int') and (p[3].types[0]=='cfloat'or p[3].types[0]=='float'):
          x=1
        elif (p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/') and (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]=='cfloat'or p[1].types[0]=='float'):
          x=2
        else:
          # print "why"
          raise TypeError("Types of expressions does not match")
      else:
        p[0].types=p[1].types
      if p[2]=='==' or p[2]=='!=' or p[2]=='<' or p[2]=='>' or p[2]=='<=' or p[2]=='>=':
        p[0].types = ['bool']
      v = newvar()
      if p[2]=='*':
        p[0].code.append(['x',v,p[1].place[0],p[3].place[0]])
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
        p[0].code.append(['=',t,'4'])
        p[0].code.append(['x',t,t,p[1].place[0]])
        p[0].code.append(['+',v,t,p[3].place[0]])
      elif (p[2]=='+'or p[2]=='-') and (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]).startswith('*'):
        t = newvar()
        p[0].code.append(['=',t,'4'])
        p[0].code.append(['x',t,t,p[3].place[0]])
        p[0].code.append(['+',v,t,p[1].place[0]])
      elif p[2]=='+' or p[2]=='-' or p[2]=='*' or p[2]=='/':
        if (p[1].types[0]=='cint'or p[1].types[0]=='int') and (p[3].types[0]=='cfloat'or p[3].types[0]=='float'):
          p[0].code.append(['typecast','float',p[1].place[0]])
          p[1].types = ['float']
          p[0].types = ['float']
          p[0].code.append([p[2]+'f',v,p[1].place[0],p[3].place[0]])
        elif (p[3].types[0]=='cint'or p[3].types[0]=='int') and (p[1].types[0]=='cfloat'or p[1].types[0]=='float'):
          p[0].code.append(['typecast','float',p[3].place[0]])
          p[3].types = ['float']
          p[0].types = ['float']
          p[0].code.append([p[2]+'f',v,p[1].place[0],p[3].place[0]])
      else:
        p[0].code.append([p[2],v,p[1].place[0],p[3].place[0]])
      p[0].place = [v]

      if not opTypeCheck(p[1].types[0],p[3].types[0],p[2]):
        raise TypeError("Expression types dont match on both side of operation "+p[2])


def p_expr_opt(p):
    '''ExpressionOpt : Expression
                     | epsilon'''
    p[0]=p[1]

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                 | UnaryOp UnaryExpr
                 | NOT UnaryExpr'''
    if len(p) == 2:
        p[0] = p[1]
        # print p[1].extra['operand']
    elif p[1] == "!":
      p[0] = p[2]
      v = newvar()
      p[0].code.append(["!",v,p[2].place[0]])
      p[0].place = [v]
    else:
      p[0] = p[2]
      v = newvar()
      if p[1][0]=='+' or p[1][0]=='-':
        v1=newvar()
        p[0].code.append(['=',v1,0])
        p[0].code.append(['=',v,v1,p[2].place[0]])
      elif p[1][0]=='*':
        p[0].code.append(['load',v,p[2].place[0]])
        if p[2].types[0][0]!='*':
          raise TypeError("Cannot refernce a non pointer")
        p[0].types[0]=p[2].types[0][1:]
      else:
        if 'AddrList' in p[0].extra:
          p[0].code.append(['addr',v,p[0].extra['AddrList'][0]])
        else:
          p[0].code.append(['addr',v,p[2].place[0]])
        # print "& case in UnaryExpr:"
        # p[0].types = []
        # print p[2].types
        # print type(p[2].types)
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
               | CreateScope Block EndScope
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
    p[0] = p[2]

def p_print_stmt(p):
  '''PrintStmt : PRINT PD Expression
               | PRINT PS Expression'''
  p[0] = p[3]
  if p[2]=="%d":
    # if p[3].types[0]!='int' and p[3].types[0]!='cint':
    #   raise TypeError("Can't Print Expr of type other than int using '%d'")
    # else:
    p[0].code.append(['printint',p[3].place[0]])
  if p[2]=="%s":
    # if p[3].types[0]!='string' and p[3].types[0]!='cstring':
    #   raise TypeError("Can't Print Expr of type other than string using '%s'")
    p[0].code.append(['printstr',p[3].place[0]])

def p_scan_stmt(p):
  '''ScanStmt : SCAN Expression'''
  p[0] = p[2]
  p[0].code.append(['scan',p[2].place[0]])
  if 'AddrList' in p[2].extra:
    p[0].code.append(['store',p[2].extra['AddrList'][0],p[2].place[0]])

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
    raise NameError("Label "+p[1]+" already exists")
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
  # print "Assignment:"
  # print p[3].types
  # print p[3].place
  # if 'retType' in p[3].extra:
  #   print "correct"
  if len(p[1].place)!=len(p[3].types):
    raise ValueError("No. of expressions on both sides of assignment are not equal")
  p[0] = node()
  p[0].code = p[1].code
  p[0].code+=p[3].code
  for i in range(len(p[1].place)):
    if p[1].types[i].startswith('c'):
      raise TypeError("Cannot assin to a const variable ")
    if p[2]=='/=':
      p[0].code.append(['/',p[1].place[i],p[1].place[i],p[3].place[i]])
    elif p[2]=='%=':
      p[0].code.append(['%',p[1].place[i],p[1].place[i],p[3].place[i]])
    elif p[2]=='*=':
      p[0].code.append(['x=',p[1].place[i],p[3].place[i]])
    else:
      p[0].code.append([p[2],p[1].place[i],p[3].place[i]])

    if p[2]=='<<=' or p[2]=='>>=':
      if p[3].types[i]!='int' and p[3].types[i]!='cint':
        raise TypeError("Operand for right/left shift is not integer")

    if p[1].extra['AddrList'][i]!='None':
      p[0].code.append(['store',p[1].extra['AddrList'][i],p[1].place[i]])

    if p[2]=='=':
      # print p[1].idlist
      # x = p[1].idlist[0]
      # info = findinfo(x)
      # print info.type
      # print p[1].types
      # scopeDict[curScope].updateExtra(p[1].idlist)
      # print i
      # print "p[1].types[i] = "+str(p[1].types[i])
      # print "p[3].types[i] = "+str(p[3].types[i])
      if not equalcheck(p[1].types[i],p[3].types[i]):
        raise TypeError("Types of expressions on both sides of = don't match")
      else:
        if p[1].types[i].startswith('*type'):
          # print "ohh -----------------------------------------"
          scopeDict[curScope].updateExtra(p[1].idlist[i],'*struct')
    else:
      if not opTypeCheck(p[1].types[i],p[3].types[i],p[2][0]):
        raise TypeError("Types of expressions on both sides of ()= don't match")

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
  ''' IfStmt : IF Expression CreateScope IFSYM Block EndScope ElseOpt '''
  p[0] = node()
  p[0].code = p[2].code
  l1 = newlabel()
  v1 = newvar()
  v2 = newvar()
  v3 = newvar()
  l2 = newlabel()
  p[0].code += [['=',v1,p[2].place[0]]]
  p[0].code += [['=',v2,'0']]
  p[0].code += [['!=',v1,v1,v2]]
  p[0].code += [['=',v3,'1']]
  p[0].code += [['-',v1,v1,v3]]
  p[0].code += [['ifgoto',v1,l1]]
  p[0].code += p[5].code
  p[0].code += [['goto',l2]]
  p[0].code += [['label',l1]]
  p[0].code += p[7].code
  p[0].code += [['label',l2]]

def p_if_sym(p):
  '''IFSYM : '''
  par = scopeDict[curScope].parent
  poff = scopeDict[par].extra['curOffset']
  scopeDict[curScope].updateExtra('curOffset',poff)

def p_else_opt(p):
  ''' ElseOpt : ELSE IfStmt
              | ELSE CreateScope Block EndScope
              | epsilon '''
  if len(p) == 3:
    p[0] = p[2]
  elif len(p)==5:
    p[0] = p[3]
  else:
    p[0]=p[1]

# ------------------- SWITCH STMT ----------------------------


def p_switch_statement(p):
  ''' SwitchStmt : ExprSwitchStmt'''
  p[0] = p[1]

def p_ExprSwitchStmt(p):
  '''ExprSwitchStmt : SWITCH Expression CreateScope LCURL StartSwitch ExprCaseClauseList RCURL EndScope'''
  p[0]=p[2]
  dLabel = None
  # print "ExprSwitchStmt:"
  # print p[6].extra['labels']
  l1 = newlabel()
  p[0].code += [['goto',l1]]
  # print p[6].code
  p[0].code += p[6].code
  p[0].code += [['label',l1]]
  p_6_rep = []
  for i in p[6].extra['exprList']:
    if len(i)!=0:
      p_6_rep.append(i)
  p[0].code += p_6_rep
  # print p[6].extra['exprList']
  for i in range(len(p[6].extra['labels'])):
    if p[6].extra['labeltype'][i] == 'default':
      dLabel = p[6].extra['labels'][i]
    else:
      v = newvar()
      p[0].code += [['==',v,p[2].place[0],p[6].place[i]]]
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
  raise ValueError("Not defined in any loop scope")

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
    # print "ExprCaseClauseList"
    if p[1].extra['labeltype'][0]=='default':
      l = newlabel()
      v = [l]
    else:
      l = p[1].extra['labels'][0]
      v =[]
      for i in range(len(p[1].extra['labels'])):
        v.append(p[1].extra['labels'][i])
      # print p[1].extra['labels']
    p[0].code = [['label',l]]
    p[0].code += p[3].code
    p[0].extra['labels'] = v
    lend = findLabel('endofAll')
    # print lend
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
        # print l
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
  '''ForStmt : FOR CreateScope ConditionBlockOpt Block EndScope'''
  p[0] = node()
  l1 = p[3].extra['before']
  p[0].code = p[3].code + p[4].code
  if 'incr' in p[3].extra:
    p[0].code += p[3].extra['incr']
  p[0].code += [['goto',l1]]
  l2 = p[3].extra['after']
  p[0].code += [['label',l2]]
  # print "For:"
  # print curScope
  # print scopeDict[curScope].extra['curOffset']
  # print scopeStack
  # vnew = newvar()
  # for x in p[3].idlist:
  #   inf = findinfo(x)
  #   print inf.offset
  #   p[0].code.append(['pop',vnew])

def p_conditionblockopt(p):
  '''ConditionBlockOpt : epsilon
             | Condition
             | ForClause'''
  p[0] = p[1]
  # print "=========="
  # print curScope
  par = scopeDict[curScope].parent
  poff = scopeDict[par].extra['curOffset']
  scopeDict[curScope].updateExtra('curOffset',poff)

def p_condition(p):
  '''Condition : Expression '''
  p[0]=p[1]
  # print p[0].idlist

def p_forclause(p):
  '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
  p[0] = p[1]
  l1 = newlabel()
  # print p[3].idlist
  # for x in p[3].idlist:
  #   if x not in p[0].idlist:
  #     p[0].idlist.append(x)
  #   inf = findinfo(x)
  #   print inf.offset
  #   p[0].code.append(['push','off_'+str(inf.offset)])
  # p[0].code +=
  p[0].code += [['label',l1]]
  p[0].extra['before'] = l1
  p[0].code += p[3].code
  l2 = newlabel()
  scopeDict[curScope].updateExtra('beginFor',l1)
  scopeDict[curScope].updateExtra('endFor',l2)
  p[0].extra['after'] = l2
  if len(p[3].place)!=0:
    v1 = newvar()
    v2 = newvar()
    p[0].code += [['=',v1,p[3].place[0]]]
    p[0].code += [['=',v2,1]]
    p[0].code += [['-',v1,v2,v2]]
    p[0].code += [['ifgoto',v1,l2]]
  p[0].extra['incr'] = p[5].code


def p_conditionopt(p):
  '''ConditionOpt : epsilon
          | Condition '''
  p[0] = p[1]


# ----------------- RETURN STMT  --------------------------

def p_return(p):
  '''ReturnStmt : RETURN ExpressionListPureOpt'''
  p[0] = p[2]
  # print p[0].types
  for scope in scopeStack[::-1]:
    if 'fName' in scopeDict[scope].extra:
      fname = scopeDict[scope].extra['fName']
      retType = scopeDict[scope].extra['retType']
  # print "retType:"
  # print retType
  if len(p[2].types) == 1:
    if not equalcheck(retType,p[2].types[0]):
      raise TypeError("Function "+fname+" has return type "+retType+" which doesnt match that in stmt i.e. "+p[2].types[0] )
    if p[2].types[0]=='int' or p[2].types[0]=='cint':
      p[0].code.append(['retint',p[2].place[0]])
    elif p[2].types[0]=='float' or p[2].types[0]=='cfloat':
      p[0].code.append(['retfloat',p[2].place[0]])
    elif p[2].types[0]=='string' or p[2].types[0]=='cstring':
      p[0].code.append(['retstring',p[2].place[0]])
    elif p[2].types[0]=='bool' or p[2].types[0]=='cbool':
      p[0].code.append(['retbool',p[2].place[0]])
  elif len(p[2].types) == 0:
    if retType!='void':
      raise TypeError("function "+fname+" has return type "+retType+" , but returned void in the stmt")
    p[0].code.append(['retvoid'])
  else:
    if len(p[2].types)!=len(retType):
      raise TypeError("Number of return argument doesn't match for "+fName)
    r = []
    # print "Return Stmt :"
    # print p[2].types
    # print retType
    # print p[2].place
    for i in range(len(p[2].types)):
      if not equalcheck(retType[i],p[2].types[i]):
        raise TypeError("Function "+fname+" has return type "+retType[i]+" which doesnt match that in stmt i.e. "+p[2].types[i] )
      # if p[2].types[i]=='int' or p[2].types[i]=='cint':
      #   p[0].code.append(['retint',p[2].place[i]])
      # elif p[2].types[i]=='float' or p[2].types[i]=='cfloat':
      #   p[0].code.append(['retfloat',p[2].place[0]])
      # elif p[2].types[i]=='string' or p[2].types[i]=='cstring':
      #   p[0].code.append(['retstring',p[2].place[i]])
      # elif p[2].types[i]=='bool' or p[2].types[i]=='cbool':
      #   p[0].code.append(['retbool',p[2].place[i]])
      r.append(p[2].place[i])
      p[0].place += r[i]
    a = ['ret_mult'] + r + []
    p[0].code.append(a)

def p_expressionlist_pure_opt(p):
  '''ExpressionListPureOpt : ExpressionList
             | epsilon'''
  p[0] = p[1]
  # print p[1].idlist

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
    '''SourceFile : PackageClause SEMICOLON ImportDeclRep TopLevelDeclRep'''
    p[0] = p[1]
    p[0].code+=p[3].code
    p[0].code+=p[4].code
    p[0].idlist += p[3].idlist
    p[0].idlist += p[4].idlist

def p_import_decl_rep(p):
  '''ImportDeclRep : epsilon
           | ImportDeclRep ImportDecl SEMICOLON'''
  if len(p) == 4:
    p[0] = p[1]
    p[0].code +=p[2].code
    p[0].idlist += p[2].idlist
  else:
    p[0] = p[1]

def p_toplevel_decl_rep(p):
  '''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SEMICOLON
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
      raise NameError("Package Name"+p[1]+"already exists")
    else:
      scopeDict[0].insert(p[1],"package")


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
  '''ImportDecl : IMPORT ImportSpec
          | IMPORT LPAREN ImportSpecRep RPAREN '''
  if len(p) == 3:
    p[0] = p[2]
  else:
    p[0] = p[3]

def p_import_spec_rep(p):
  ''' ImportSpecRep : ImportSpecRep ImportSpec SEMICOLON
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
  # print p[1]

# ---------------   EMPTY and SYNTAX ERROR --------------

def p_empty(p):
  '''epsilon : '''
  p[0] = node()


def p_error(p):
    if p:
      print("Syntax error at line no:", (p.lineno-13), "at position", p.lexpos, "in the code.   " "TOKEN VALUE=", p.value,  "TOKEN TYPE=" ,p.type)
      parser.errok()
    else:
      print("Syntax error at EOF")



parser = yacc.yacc()


try:
  s = data
except EOFError:
  print("EOF Error")
if not s:
  print("Not found")
result = parser.parse(s,debug=0)



# print "\nPrinting the identifiers used:"
# print result.idlist

# print "\nPrinting the 3AC code for the input:"
# print_list(result.code)

# print result.__dict__

# print "Successfully Done <---------------->"


# print_scope_Dict()


def print_in_format():
  # print "Scope,\t\t\tName,\t\t\tType,\t\t\tOffset,\t\t\tChild"
  tab = [[]]
  tab[0] = ['Scope,','Name,','Type,','Offset,','Child']
  for i in range(len(scopeDict)):
    # print "Level "+str(i)+" :"
    # print scopeDict[i].__dict__
    symtab = scopeDict[i]
    # print ""
    for j in symtab.symbols:
      s = ""
      t = symtab.table[j].type
      if type(t) is list:
        for k in t:
          # print k[:4]
          if k[:4]=="type":
            k = 'struct'
          if k[:5]=='*type':
            k='*struct'
          s += str(k)+"_"
        s = s[:-1]
      else:
        k = t
        if k[:4]=="type":
          k = 'struct'
        if k[:5]=='*type':
          k='*struct'
        s = k
      scope = str(i)
      name = j
      typ = s
      off = str(symtab.table[j].offset)
      if symtab.table[j].child:
        child = str(symtab.table[j].child.val)
      else:
        child = ""
      # print scope+",\t\t\t"+name+ ",\t\t\t"+typ+",\t\t\t"+off+",\t\t\t"+ child
      tab.append([scope+',',name+',',typ+',',off+',',child])
    # info = scopeDict[i].retrieve()
    # print " <----------------------------------> "
  # print tab
  col_width = max(len(word) for row in tab for word in row) + 5
  flag = 0
  for row in tab:
    print "".join(word.ljust(col_width) for word in row)

# csv_name = file_name[:-3]
# print csv_name
sys.stdout =  open("Table.csv", "w+")
print_in_format()

# info1 = findinfo('i',2)
# print info1.mysize

def print_3AC(l):
  for i in l:
    s = ""
    for j in i:
      s+=str(j)+" "
    print s


sys.stdout =  open("3AC.txt", "w+")
print_3AC(result.code)

# print "FINAL CODE:"
# print_list(result.code)


# print scopeDict[2].__dict__

# info2 = findinfo('age',2)
# print "Offset of age in rect :"
# print info2.offset


