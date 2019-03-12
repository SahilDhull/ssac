#!/usr/bin/env python2
import ply.yacc as yacc
import sys
import os
from lexer import *
from symbol import *
# from scope import *

root = None

# ----------  TYPE CHECKING -------------------

def equalcheck(x,y):
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
labelNum = 1
mainFunc = True

labelDict = {}
scopeDict = {}
scopeDict[0] = st()
scopeStack=[0]

def addscope(name=None):
  # print name
  global scopeLevel
  global curScope
  scopeLevel+=1
  scopeStack.append(scopeLevel)
  scopeDict[scopeLevel] = st()
  scopeDict[scopeLevel].setParent(curScope)
  if name is not None:
    # Not sure if correct
    if type(name) is list:
      scopeDict[curScope].insert(name[1],'func')
      scopeDict[curScope].insert(name[1],'child',scopeDict[scopeLevel])
    else:
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

def newlabel():
  global labelNum
  val = 'l'+str(labelNum)
  labelNum+=1
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
        elif p[1]=='bool':
          p[0].size=[1]
        else:
          p[0].size = [8]
          # maximum size of string set to 8 bytes
    else:
        if not definedcheck(p[2]):
          raise TypeError("TypeName" + p[2] + "not defined anywhere")
        else:
          p[0]=node()
          var = findinfo(p[2],0)
          p[0].types.append(var.type)

def p_type_lit(p):
    '''TypeLit : ArrayType
               | StructType
               | PointerType
               | MapType
               | SliceType'''
    p[0] = p[1]

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
# to change, not fully correct right now

def p_array_type(p):
  '''ArrayType : LSQUARE ArrayLength RSQUARE ElementType'''
  p[0] = node()
  p[0].code = p[2].code + p[4].code
  # print "ArrayType => "+p[4].idlist[0]
  # ----- changing it ---------------
  p[0].types.append("*"+p[4].types[0])
  # ---------------------------------
  # if p[4].types[0]=='arr':
  #   p[0].types = ['arr'] + p[4].types[1:]
  # else:
  #   p[0].types = ['arr'] + p[4].types
  #   # print p[0].types[1:]
  # ---------------------------------
  v = newvar()
  p[0].code.append(['=',v,p[2].place[0]])
  if 'operandValue' in p[2].extra:
    # print "excellent"
    p[0].extra['operandValue'] = p[2].extra['operandValue']
  # print p[4].extra
  p[0].size = [v] + p[4].size
  #TODO

def p_array_length(p):
  ''' ArrayLength : Expression '''
  p[0]=p[1]

def p_element_type(p):
  ''' ElementType : Type '''
  p[0]=p[1]

# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
  '''StructType : FuncScope STRUCT LCURL FieldDeclRep RCURL'''
  p[0] = p[4]
  info = findinfo(p[-1],0)
  p[0].types = [info.type]

def p_func_scope(p):
  '''FuncScope : '''
  addscope(p[-1])


def p_field_decl_rep(p):
  ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
                  | epsilon '''
  if len(p) == 4:
    # addinstance(p[0],p[1],p[2])
    p[0] = p[1]
    p[0].types+=p[2].types
    p[0].code+=p[2].code
    p[0].idlist+=p[2].idlist
  else:
    p[0]=p[1]

def p_field_decl(p):
  ''' FieldDecl : IdentifierList Type'''
  p[0] = p[1]
  for i in p[0].idlist:
    # print p[2].types[0]
    scopeDict[curScope].updateAttr(i,'type',p[2].types[0])


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MULTIPLY BaseType'''
    p[0] = p[2]
    p[0].size = ['inf']+p[0].size
    p[0].types[0]="*"+p[0].types[0]

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
      p[1].place[i] = p[2].place[i]
      scope = findscope(x)
      scopeDict[scope].updateAttr(x,'place',p[1].place[i])
      if p[2].types[i]==i:
        raise TypeError('Type of ' + p[0].idlist[i] + 'does not match that of expr')
      scopeDict[scope].updateAttr(x,'type',p[2].types[i])


def p_type_expr_list(p):
    '''TypeExprListOpt : Type EQUALS ExpressionList
                       | epsilon'''
    if len(p) == 4:
      p[0]=p[3]
      flag=0
      for i in range(len(p[0].place)):
        if not equalcheck(p[1].types[0],p[3].types[i]):
          p[0].types[i] = i
          flag=1
        else:
          p[0].types[i]=p[1].types[0]
    else:
      p[0]=p[1]


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
    else:
        p[0] = p[3]

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                  | epsilon'''
    if len(p) == 4:
        p[0] = p[1]
        p[0].code+=p[2].code
    else:
        p[0]=p[1]

def p_var_spec(p):
  '''VarSpec : IdentifierList Type ExpressionListOpt'''
  if len(p[3].place)==0:
    p[0]=p[1]
    p[0].code+=p[2].code
    # print "VarSpec : "
    # print p[1].idlist
    # print p[2].types
    # print p[2].size
    if p[2].types[0][0]=='*':
      v = newvar()
      if p[2].size[0]!='inf':
        p[0].code.append(['=',v,1])
      for i in p[2].size:
        if p[2].size[0]!='inf':
          p[0].code.append(['x=',v,i])

    for i in range(len(p[1].idlist)):
      x = p[1].idlist[i]
      s = findscope(x)
      scopeDict[s].updateAttr(x,'type',p[2].types[0])
      #REMAINING -- For arrays   #CODGEN
      if p[2].types[0][0] == '*' and p[2].size[0]!='inf':
        if 'operandValue' in p[2].extra:
          info1 = findinfo(x)
          # print x
          # print p[2].extra['operandValue']
          scopeDict[curScope].updateExtra(str(x),p[2].extra['operandValue'][0])
        p[0].code.append(['array',p[1].place[i],v])
        scopeDict[s].updateAttr(p[1].idlist[i],'size',p[2].size)
    return
  p[0]=node()
  p[0].code = p[1].code + p[3].code
  if len(p[1].place)!=len(p[3].place):
    raise ValueError("Mismatch in number of expressions assigned to variables")

  for i in range(len(p[1].place)):
    x = p[1].idlist[i]
    p[1].place[i] = p[3].place[i]
    scope = findscope(x)
    scopeDict[scope].updateAttr(x,'place',p[1].place[i])
    scopeDict[scope].updateAttr(x,'type',p[2].types[0])
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
  p[0].code.append(['=',v,p[3].place[0]])
  scopeDict[curScope].updateAttr(p[1],'place',v)
  scopeDict[curScope].updateAttr(p[1],'type',p[3].types[0])
  

# -------------------------------------------------------



# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
  '''FunctionDecl : FUNC FunctionName CreateScope Function EndScope
                  | FUNC FunctionName CreateScope Signature EndScope'''
  p[0]=node()
  if len(p[4].code):
    global mainFunc
    if mainFunc:
      mainFunc = False
      p[0].code = [["goto","l0"]]
    info = findinfo(p[2])
    label = info.label
    p[0].code.append(['label',label])
    p[0].code += p[4].code
    # p[0].idlist += p[4].idlist
    # print p[4].idlist
  p[0].idlist += [p[2]]

def p_create_scope(p):
  '''CreateScope : '''
  addscope()

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
    for i in range(len(p[1].idlist)):
      x = p[1].idlist[i]
      info = findinfo(x)
      p[0].code = [['pload',info.place,len(p[1].idlist)-i-1]] + p[0].code
    if checksignature(p[-2]):
      if p[-2]=="main":
        scopeDict[0].updateAttr('main','label','l0')
        scopeDict[0].updateAttr('main','child',scopeDict[curScope])
      info = findinfo(p[-2])
      info.type = 'func'
    else:
      raise NameError('No Signature found for '+p[-2])


def p_ret_type_set(p):
  '''RetTypeSet : '''
  fname = p[-1].extra['fName']
  scopeDict[curScope].updateExtra('fName',fname)
  if len(p[-1].types)>0:
    scopeDict[curScope].updateExtra('retType',p[-1].types[0])
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
  v = newvar()
  # print "BasicLit : "
  # print p[2]
  p[0].code.append(["=",v,p[2]])
  p[0].place.append(v)
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
  if info.type=='func' or info.type=='sigType':
    p[0].types = [info.retType]
    p[0].place.append(info.label)
  else:
    # print "OperandName"
    # print p[1]
    # print info.type
    # print info.listsize
    p[0].types = [info.type]
    p[0].place.append(info.place)
    p[0].extra['layerNum'] = 0
    p[0].extra['operand'] = p[1]
    if info.listsize is not None:
      p[0].size = info.listsize
    else:
      for i in range(len(info.type)):
        if info.type[i]!='*':
          break;
      if info.type[i:]=='int':
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
                 | PrimaryExpr Selector
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
    info = findinfo(p[1].extra['operand'])
    # print info.type
    lsize = info.listsize
    #DOUBT
    # print "PrimaryExpr : lsize = "
    # print p[3].types
    # print lsize
    # print p[1].extra['layerNum']
    #CHECK
    if 'operandValue' in p[3].extra:
      # for arrays of single dimension
      # print "fantastic -- PrimaryExpr"
      z = p[3].extra['operandValue'][0]
      # print lsize
      y = scopeDict[curScope].extra[p[1].extra['operand']]
      if z>=y:
        raise IndexError("Array "+ p[1].extra['operand'] +" out of Bounds")
    if p[1].extra['layerNum'] == len(lsize):
      raise IndexError('Dimension of array '+p[1].extra['operand'] + ' doesnt match')

    v1 = newvar()
    p[0].code.append(['=',v1,p[3].place[0]])
    for i in lsize[p[1].extra['layerNum']:]:
      # print "i = "+i
      p[0].code.append(['x=',v1,i])
    v2 = newvar()
    p[0].code.append(['+',v2,p[0].place[0],v1])
    p[0].place = [v2]
    #CHECK
    if p[1].extra['layerNum'] == len(lsize)-1:
      v3 = newvar()
      p[0].code.append(['load',v3,v2])
      p[0].place = [v3]
    p[0].extra['AddrList'] = [v2]
    p[0].types = [p[1].types[0][1:]]
    p[0].extra['layerNum'] += 1
  elif p[2]=='(':
    p[0]=p[1]
    p[0].code+=p[3].code

    listval = []

    for key,value in enumerate(scopeDict[curScope].table):
      cur = findinfo(value,curScope)
      listval.append(value)
      p[0].code.append(['push',cur.place])

    info = findinfo(p[1].idlist[0],0)
    functionDict = info.child
    paramTypes = functionDict.extra['types']
    if len(p[3].place):
      for x in p[3].place:
        p[0].code.append(['push',x])
      for i in range(len(p[3].place)):
        if not equalcheck(paramTypes[i],p[3].types[i]):
          raise TypeError("Type Mismatch in "+p[1].idlist[0])

    # Checking Return Type
    if len(info.retType)==1:
      if info.retType[0]=='void':
        p[0].code.append(['callvoid',info.label])
      elif info.retType[0]=='int':
        v1 = newvar()
        p[0].place = [v1]
        p[0].code.append(['callint',v1,info.label])
      p[0].types = [p[1].types[0]]
    # else:
      # Check for Multiple Return Types
      #TODO

    var1 = newvar()
    if len(p[3].place):
      for x in p[3].place:
        p[0].code.append(['pop',var1])

    for val in listval[::-1]:
      cur = findinfo(val,curScope)
      p[0].code.append(['pop',cur.place])

  else:
    if not len(p[2].place):
      p[0] =node()
    else:
      p[0] = p[1]
      p[0].place = p[2].place
      p[0].types = p[2].types


def p_selector(p):
    '''Selector : DOT IDENTIFIER'''
    p[0] = node()
    info = findinfo(p[-1].idlist[0])
    structname=info.type
    for i in range(len(structname)):
      if structname[i]!='*':
        break
    structname = structname[i+4:]
    # print "Selector"
    # print structname
    info_of_struct = findinfo(structname,0)
    struct_scope = info_of_struct.child
    if p[2] not in struct_scope.table:
      raise NameError("identifier " + p[2]+ " is not defined inside the struct")
    s = p[-1].idlist[0]+'.'+p[2]
    if checkid(s,'e'):
      info = findinfo(s)
      p[0].place = [info.place]
      p[0].types = [info.type]
    else:
      v = newvar()
      p[0].place = [v]
      type_of_var = struct_scope.retrieve(p[2])
      p[0].types = [type_of_var.type]
      scopeDict[curScope].insert(s,p[0].types[0])
      scopeDict[curScope].updateAttr(s,'place',p[0].place[0])

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
    print "Type Assertion Not Implemented (Interface also not Implemented"

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
      if p[2]=='<<' or p[2]=='>>'and p[3].types[0]!='int' and p[3].types[0]!='cint':
          raise TypeError("RHS of shift operator is not integer")
      if not opTypeCheck(p[1].types[0],p[3].types[0],'.'):
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
        p[0].types[0] = '*' + p[2].types[0]
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
  if len(p[1].place)!=len(p[3].place):
    raise ValueError("No. of expressions on both sides of assignment are not equal")
  p[0] = node()
  p[0].code = p[1].code
  p[0].code+=p[3].code
  for i in range(len(p[1].place)):
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
      # print i
      # print "p[1].types[i] = "+str(p[1].types[i])
      # print "p[3].types[i] = "+str(p[3].types[i])
      if not equalcheck(p[1].types[i],p[3].types[i]):
        raise TypeError("Types of expressions on both sides of = don't match")
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
  ''' IfStmt : IF Expression CreateScope Block EndScope ElseOpt '''
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
  p[0].code += p[4].code
  p[0].code += [['goto',l2]]
  p[0].code += [['label',l1]]
  p[0].code += p[6].code
  p[0].code += [['label',l2]]

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
  '''ExprSwitchStmt : SWITCH Expression CreateScope LCURL StartSwitch ExprCaseClauseList RCURL '''
  p[0]=p[2]
  dLabel = None
  l1 = newlabel()
  p[0].code += [['goto',l1]]
  p[0].code += p[6].code
  p[0].code += [['label',l1]]
  p[0].code += p[6].extra['exprList']
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
    l = newlabel()
    p[0].code = [['label',l]]
    p[0].code += p[3].code
    p[0].extra['labels'] = [l]
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
        for i in range(len(p[2].place)):
          l = newlabel()
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

def p_conditionblockopt(p):
  '''ConditionBlockOpt : epsilon
             | Condition
             | ForClause'''
  p[0] = p[1]

def p_condition(p):
  '''Condition : Expression '''
  p[0]=p[1]

def p_forclause(p):
  '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
  p[0] = p[1]
  l1 = newlabel()
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

  for scope in scopeStack[::-1]:
    if 'fName' in scopeDict[scope].extra:
      fname = scopeDict[scope].extra['fName']
      retType = scopeDict[scope].extra['retType']
  if len(p[2].types) == 1:
    if not equalcheck(retType,p[2].types[0]):
      raise TypeError("Function "+fname+" has return type "+retType+" which doesnt match that in stmt i.e. "+p[2].types[0] )
    p[0].code.append(['retint',p[2].place[0]])
  elif len(p[2].types) == 0:
    if retType!='void':
      raise TypeError("function "+fname+" has return type "+retType+" , but returned void in the stmt")
    p[0].code.append(['retvoid'])

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

def print_list(l):
  for i in l:
    print i

print "\nPrinting the identifiers used:"
print result.idlist

print "\nPrinting the 3AC code for the input:"
print_list(result.code)
