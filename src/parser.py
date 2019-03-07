#!/usr/bin/env python2
import ply.yacc as yacc
import sys
import os
from lexer import *
from pprint import pprint

# class Node:
#    def __init__(self,type,children=None,leaf=None):
#         self.type = type
#         if children:
#              self.children = children
#         else:
#              self.children = [ ]
#         self.leaf = leaf



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


# ------------------------START----------------------------
def p_start(p):
    '''start : SourceFile'''
    # p[0] = ["start", p[1]]
    p[0] = p[1]
    p[0][0] = "start"
    # print p[0]
# -------------------------------------------------------


# -----------------------TYPES---------------------------
def p_type(p):
    '''Type : TypeName
            | TypeLit'''
    if len(p) == 4:
        p[0] = ["Type", "(", p[2], ")"]
    else:
        # p[0] = ["Type", p[1]]
        p[0]=p[1]

def p_type_name(p):
    '''TypeName : TypeToken
                | QualifiedIdent'''
    # p[0] = ["TypeName", p[1]]
    p[0]=p[1]

def p_type_token(p):
    '''TypeToken : INT_T
                 | INT
                 | FLOAT
                 | BOOL
                 | COMPLEX
                 | BOOL_T
                 | COMPLEX_T
                 | STRING
                 | FLOAT_T
                 | STRING_T
                 | TYPE IDENTIFIER'''
    if len(p) == 2:
        # p[0] = ["TypeToken", p[1]]
        p[0]=p[1]
    else:
        p[0] = ["TypeToken", p[1], p[2]]

def p_type_lit(p):
    '''TypeLit : ArrayType
               | StructType
               | PointerType
               | MapType
               | SliceType'''
    # p[0] = ["TypeLit", p[1]]
    p[0] = p[1]
    p[0][0] = "TypeLit"

def p_type_opt(p):
    '''TypeOpt : Type
               | epsilon'''
    # p[0] = ["TypeOpt", p[1]]
    p[0] = p[1]
    # p[0][0] = "TypeOpt"
# -------------------------------------------------------

def p_slice_type(p):
    '''SliceType : LSQUARE RSQUARE ElementType'''
    p[0] = ["SliceType","[","]",p[3]]


# ----------------- channel type -----------------------

# def p_channel_type(p):
#     '''ChannelType : CHAN ElementType
#                    | CHAN LEFT_ARROW ElementType
#                    | LEFT_ARROW CHAN ElementType'''
#     if len(p) == 3:
#         p[0] = ["ChannelType","chan",p[2]]
#     elif p[1] == "<-":
#         p[0] = ["ChannelType","<-","chan",p[3]]
#     else:
#         p[0] = ["ChannelType","chan","<-",p[3]]

# ------------------------------------------------------

# ------------------ map type --------------------------

def p_map_type(p):
  '''MapType : MAP LSQUARE KeyType RSQUARE ElementType '''
  p[0] = ["MapType","map","[",p[2],"]",p[4]]

def p_key_type(p):
  '''KeyType : Type'''
  # p[0] = ["KeyType",p[1]]
  p[0] = p[1]
  # p[0][0] = "KeyType"

# ------------------------------------------------------

# ------------------- ARRAY TYPE -------------------------
def p_array_type(p):
  '''ArrayType : LSQUARE ArrayLength RSQUARE ElementType'''
  p[0] = ["ArrayType", "[", p[2], "]", p[4]]

def p_array_length(p):
  ''' ArrayLength : Expression '''
  # p[0] = ["ArrayLength", p[1]]
  p[0]=p[1]

def p_element_type(p):
  ''' ElementType : Type '''
  # p[0] = ["ElementType", p[1]]
  p[0]=p[1]

# --------------------------------------------------------


# ----------------- STRUCT TYPE ---------------------------
def p_struct_type(p):
  '''StructType : STRUCT LCURL FieldDeclRep RCURL'''
  p[0] = ["StructType", "struct", "{", p[3], "}"]

def p_field_decl_rep(p):
  ''' FieldDeclRep : FieldDeclRep FieldDecl SEMICOLON
                  | epsilon '''
  if len(p) == 4:
    p[0] = ["FieldDeclRep", p[1], p[2], ";"]
  else:
    # p[0] = ["FieldDeclRep", p[1]]
    p[0]=p[1]

def p_field_decl(p):
  ''' FieldDecl : IdentifierList Type TagOpt'''
  p[0] = ["FieldDecl", p[1], p[2], p[3]]

def p_TagOpt(p):
  ''' TagOpt : Tag
             | epsilon '''
  # p[0] = ["TagOpt", p[1]]
  p[0]=p[1]

def p_Tag(p):
  ''' Tag : STRING_LIT '''
  # p[0] = ["Tag", p[1]]
  p[0]=p[1]
# ---------------------------------------------------------


# ------------------POINTER TYPES--------------------------
def p_point_type(p):
    '''PointerType : MULTIPLY BaseType'''
    p[0] = ["PointerType", "*", p[2]]

def p_base_type(p):
    '''BaseType : Type'''
    p[0]=p[1]
# ---------------------------------------------------------


# ---------------FUNCTION TYPES----------------------------
def p_sign(p):
    '''Signature : Parameters ResultOpt'''
    if len(p[2]) == 0:
        p[0]=p[1]
    else:
        p[0] = ["Signature", p[1], p[2]]

def p_result_opt(p):
    '''ResultOpt : Result
                 | epsilon'''
    # p[0] = ["ResultOpt", p[1]]
    p[0]=p[1]
    # if p[0] == "epsilon":
    #     p[0] = [""]

def p_result(p):
    '''Result : Parameters
              | Type'''
    p[0]=p[1]

# ------------------ to change -----------------



###########################      SAHIL          ########################
def p_params(p):
    '''Parameters : LPAREN ParametersList RPAREN
                  | LPAREN ParametersList COMMA RPAREN
                  | LPAREN RPAREN'''
    if len(p) == 4:
      p[0] = ["Parameters","(",p[2],")"]
    elif len(p) == 5:
      p[0] = ["Parameters","(",p[2],",",")"]
    else:
      p[0] = ["Parameters","(",")"]

def p_param_list(p):
    '''ParametersList : ParameterDecl
                      | ParametersList COMMA ParameterDecl'''
    if len(p) == 2:
      p[0]=p[1]
      # p[0] = p[1]
    else:
      p[0] = ["ParametersList",p[1],",",p[3]]



def p_param_decl(p):
    '''ParameterDecl : DOTS Type
                     | IdentifierList Type
                     | IdentifierList DOTS Type
                     | Type'''
    if len(p) == 3:
      if p[1] == "...":
        p[0] = ["ParameterDecl","...",p[2]]
      else:
        p[0] = ["ParameterDecl",p[1],p[2]]
    elif len(p) == 2:
      p[0]=p[1]
    else:
      p[0] = ["ParameterDecl",p[1],"...",p[3]]

# def p_ohh(p):
#     '''Ohh : Type'''
#     p[0]=p[1]

# -----------------------------------------------------


# ---------------------------------------------------------


#-----------------------BLOCKS---------------------------
def p_block(p):
    '''Block : LCURL StatementList RCURL'''
    p[0] = ["Blocks", "{" , p[2], "}"]

def p_stat_list(p):
    '''StatementList : StatementRep'''
    # p[0] = ["StatementList", p[1]]
    p[0] = p[1]

def p_stat_rep(p):
    '''StatementRep : StatementRep Statement SEMICOLON
                    | epsilon'''
    if len(p) == 4:
        p[0] = ["StatementRep", p[1], p[2], ';']
    else:
        # p[0] = ["StatementRep", p[1]]
        p[0] = p[1]
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
  # p[0] = ["TopLevelDecl", p[1]]
  p[0] = p[1]
  # p[0][0] = "TopLevelDecl"
# -------------------------------------------------------


# ------------------CONSTANT DECLARATIONS----------------
def p_const_decl(p):
    '''ConstDecl : CONST ConstSpec
                 | CONST LPAREN ConstSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = ["ConstDecl", "const", p[2]]
    else:
        p[0] = ["ConstDecl", "const", '(', p[3], ')']

def p_const_spec_rep(p):
    '''ConstSpecRep : ConstSpecRep ConstSpec SEMICOLON
                    | epsilon'''
    if len(p) == 4:
        p[0] = ["ConstSpecRep", p[1], p[2], ';']
    else:
        # p[0] = ["ConstSpecRep", p[1]]
        p[0]=p[1]

def p_const_spec(p):
    '''ConstSpec : IdentifierList TypeExprListOpt'''
    p[0] = ["ConstSpec", p[1], p[2]]

def p_type_expr_list(p):
    '''TypeExprListOpt : TypeOpt EQUALS ExpressionList
                       | epsilon'''
    if len(p) == 4:
        p[0] = ["TypeExprListOpt", p[1], "=", p[3]]
    else:
        # p[0] = ["TypeExprListOpt", p[1]]
        p[0]=p[1]


def p_identifier_list(p):
    '''IdentifierList : IDENTIFIER 
                      | IdentifierRep'''
    # p[0] = ["IdentifierList", p[1]]
    p[0]=p[1]

def p_identifier_rep(p):
    '''IdentifierRep : IdentifierRep COMMA IDENTIFIER
                     | IDENTIFIER COMMA IDENTIFIER'''
    if len(p) == 4:
        p[0] = ["IdentifierRep", p[1], ",", p[3]]
    else:
        p[0]=p[1]


def p_expr_list(p):
    '''ExpressionList : Expression ExpressionRep'''
    if len(p[2]) == 0:
        p[0]=p[1]
    else:
        p[0] = ["ExpressionList", p[1], p[2]]

def p_expr_rep(p):
    '''ExpressionRep : ExpressionRep COMMA Expression
                     | epsilon'''
    if len(p) == 4:
        # p[0] = ["ExpressionRep", p[1], ',', p[3]]
        p[0] = [',', p[1], p[3]]
    else:
        # p[0] = ["ExpressionRep", p[1]]
        p[0]=p[1]
# -------------------------------------------------------


# ------------------TYPE DECLARATIONS-------------------
def p_type_decl(p):
    '''TypeDecl : TYPE TypeSpec
                | TYPE LPAREN TypeSpecRep RPAREN'''
    if len(p) == 5:
        p[0] = ["TypeDecl", "type", "(", p[3], ")"]
    else:
        p[0] = ["TypeDecl", "type", p[2]]

def p_type_spec_rep(p):
    '''TypeSpecRep : TypeSpecRep TypeSpec SEMICOLON
                   | epsilon'''
    if len(p) == 4:
        p[0] = ["TypeSpecRep", p[1], p[2], ";"]
    else:
        # p[0] = ["TypeSpecRep", p[1]]
        p[0]=p[1]

def p_type_spec(p):
    '''TypeSpec : AliasDecl
                | TypeDef'''
    p[0]=p[1]
def p_alias_decl(p):
    '''AliasDecl : IDENTIFIER EQUALS Type'''
    p[0] = ["AliasDecl", p[1], '=', p[3]]
# -------------------------------------------------------


# -------------------TYPE DEFINITIONS--------------------
def p_type_def(p):
    '''TypeDef : IDENTIFIER Type'''
    p[0] = ["TypeDef", p[1], p[2]]
# -------------------------------------------------------


# ----------------VARIABLE DECLARATIONS------------------
def p_var_decl(p):
    '''VarDecl : VAR VarSpec
               | VAR LPAREN VarSpecRep RPAREN'''
    if len(p) == 3:
        p[0] = ["VarDecl", "var", p[2]]
    else:
        p[0] = ["VarDecl", "var", "(", p[3], ")"]

def p_var_spec_rep(p):
    '''VarSpecRep : VarSpecRep VarSpec SEMICOLON
                  | epsilon'''
    if len(p) == 4:
        p[0] = ["VarSpecRep", p[1], p[2], ";"]
    else:
        # p[0] = ["VarSpecRep", p[1]]
        p[0]=p[1]

def p_var_spec(p):
    '''VarSpec : IdentifierList Type ExpressionListOpt
               | IdentifierList EQUALS ExpressionList'''
    if p[2] == '=':
        p[0] = ["VarSpec", p[1], "=", p[3]]
    else:
        p[0] = ["VarSpec", p[1], p[2], p[3]]

def p_expr_list_opt(p):
    '''ExpressionListOpt : EQUALS ExpressionList
                         | epsilon'''
    if len(p) == 3:
        # p[0] = ["ExpressionListOpt", "=", p[2]]
        p[0] = ["=", p[2]]
    else:
        # p[0] = ["ExpressionListOpt", p[1]]
        p[0]=p[1]
# -------------------------------------------------------


# ----------------SHORT VARIABLE DECLARATIONS-------------
def p_short_var_decl(p):
  ''' ShortVarDecl : IDENTIFIER SHORT_ASSIGNMENT Expression '''
  p[0] = ["ShortVarDecl", p[1], ":=", p[3]]
# -------------------------------------------------------



# ----------------FUNCTION DECLARATIONS------------------
def p_func_decl(p):
    '''FunctionDecl : FUNC FunctionName Function
                    | FUNC FunctionName Signature'''
    p[0] = ["FunctionDecl", "func", p[2], p[3]]

def p_func_name(p):
    '''FunctionName : IDENTIFIER'''
    # p[0] = ["FunctionName", p[1]]
    p[0] = p[1]
    # p[0][0] = "FunctionName"

def p_func(p):
    '''Function : Signature FunctionBody'''
    p[0] = ["Function", p[1], p[2]]

def p_func_body(p):
    '''FunctionBody : Block'''
    # p[0] = ["FunctionBody", p[1]]
    p[0] = p[1]
    p[0][0] = "FunctionBody"
# -------------------------------------------------------


# ----------------------OPERAND----------------------------
def p_operand(p):
    '''Operand : Literal
               | OperandName
               | LPAREN Expression RPAREN'''
    if len(p) == 2:
        # p[0] = ["Operand", p[1]]
        p[0] = p[1]
        # p[0][0] = "Operand"
    else:
        p[0] = ["Operand", "(", p[2], ")"]

def p_literal(p):
    '''Literal : BasicLit
               | CompositeLit'''
    # p[0] = ["Literal", p[1]]
    p[0] = p[1]
    # p[0][0] = "Literal"

# -------------   composite literals --------------------

def p_composite_lit(p):
  '''CompositeLit : LiteralType LiteralValue'''
  p[0] = ["CompositeLit",p[1],p[2]]

def p_literal_type(p):
  '''LiteralType : StructType
                 | ArrayType
                 | SliceType
                 | MapType
                 | TypeName'''
  p[0]=p[1]

def p_literal_value(p):
  '''LiteralValue : LCURL RCURL
                  | LCURL ElementList RCURL
                  | LCURL ElementList COMMA RCURL'''
  if len(p)==3:
    p[0]=["LiteralValue","{","}"]
  elif len(p)==4:
    p[0]=["LiteralValue","{",p[2],"}"]
  else:
    p[0]=["LiteralValue","{",p[2],p[3],"}"]

def p_element_list(p):
  '''ElementList : KeyedElement
                 | ElementList COMMA KeyedElement'''
  if len(p)==2:
    p[0]=p[1]
  else:
    p[0]=[",",p[1],p[3]]

# def p_comma_keyed(p):
#   '''CommaKeyed : CommaKeyed COMMA KeyedElement
#                 | epsilon'''
#   if len(p)==2:
#     p[0]=p[1]
#   else:
#     p[0]=["CommaKeyedElement",",",p[2],p[3]]

def p_keyed_element(p):
  '''KeyedElement : Element
                  | Key COLON Element
                  | IDENTIFIER COLON Element'''
  if len(p)==2:
    p[0]=p[1]
  else:
    p[0]=["KeyedElement",p[1],":",p[3]]

def p_key(p):
  '''Key : Expression
         | LiteralValue'''
  p[0]=p[1]

def p_element(p):
  '''Element : Expression
             | LiteralValue'''
  p[0]=p[1]

# -------------------------------------------------------

def p_basic_lit(p):
    '''BasicLit : INT_LIT
                | FLOAT_LIT
                | IMAGINARY_LIT
                | STRING_LIT'''
    # p[0] = ["BasicLit",str(p[1])]
    p[0]=[str(p[1])]

def p_operand_name(p):
    '''OperandName : IDENTIFIER'''
    # p[0] = ["OperandName", p[1]]
    p[0] = p[1]
# ---------------------------------------------------------


# -------------------QUALIFIED IDENTIFIER----------------
def p_quali_ident(p):
    '''QualifiedIdent : IDENTIFIER DOT TypeName'''
    p[0] = ["QualifiedIdent", p[1], ".", p[3]]
# -------------------------------------------------------


# ------------------PRIMARY EXPRESSIONS--------------------
def p_prim_expr(p):
    '''PrimaryExpr : Operand
                   | PrimaryExpr Selector
                   | Conversion
                   | PrimaryExpr Index
                   | PrimaryExpr Slice
                   | PrimaryExpr TypeAssertion
                   | PrimaryExpr Arguments'''
    if len(p) == 2:
        # p[0] = ["PrimaryExpr", p[1]]
        p[0] = p[1]
        # p[0][0] = "PrimaryExpr"
    else:
        p[0] = ["PrimaryExpr", p[1], p[2]]

def p_selector(p):
    '''Selector : DOT IDENTIFIER'''
    p[0] = ["Selector", ".", p[2]]
    # p[0] = p[1]
    # p[0][0] = "Selector"

def p_index(p):
    '''Index : LSQUARE Expression RSQUARE'''
    p[0] = ["Index", "[", p[2], "]"]

def p_slice(p):
    '''Slice : LSQUARE ExpressionOpt COLON ExpressionOpt RSQUARE
             | LSQUARE ExpressionOpt COLON Expression COLON Expression RSQUARE'''
    if len(p) == 6:
        p[0] = ["Slice", "[", p[2], ":", p[4], "]"]
    else:
        p[0] = ["Slice", "[", p[2], ":", p[4], ":", p[6], "]"]

def p_type_assert(p):
    '''TypeAssertion : DOT LPAREN Type RPAREN'''
    p[0] = ["TypeAssertion", ".", "(", p[3], ")"]

def p_argument(p):
    '''Arguments : LPAREN ExpressionListTypeOpt RPAREN'''
    p[0] = ["Arguments", "(", p[2], ")"]

def p_expr_list_type_opt(p):
    '''ExpressionListTypeOpt : ExpressionList
                             | epsilon'''
    if len(p) == 3:
        p[0] = ["ExpressionListTypeOpt", p[1], p[2]]
    else:
        # p[0] = ["ExpressionListTypeOpt", p[1]]
        p[0] = p[1]
        # p[0][0] = "ExpressionListTypeOpt"



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
    if len(p) == 4:
        # p[0] = ["Expression", p[1], p[2], p[3]]
        p[0] = [str(p[2]), p[1], p[3]]
    else:
        # p[0] = ["Expression", p[1]]
        p[0] = p[1]
        # p[0][0] = "Expression"



def p_expr_opt(p):
    '''ExpressionOpt : Expression
                     | epsilon'''
    # p[0] = ["ExpressionOpt", p[1]]
    p[0]=p[1]

def p_unary_expr(p):
    '''UnaryExpr : PrimaryExpr
                 | UnaryOp UnaryExpr
                 | NOT UnaryExpr'''
    if len(p) == 2:
        # p[0] = ["UnaryExpr", p[1]]
        p[0] = p[1]
        # p[0][0] = "UnaryExpr"
    elif p[1] == "!":
        p[0] = ["UnaryExpr", "!", p[2]]
    else:
        # p[0] = ["UnaryExpr", p[1], p[2]]
        p[0] = [p[1],p[2]]

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
    p[0] = ["Conversion", "typecast", p[2],  "(", p[4], ")"]
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
                 | Block
                 | IfStmt
                 | SwitchStmt
                 | ForStmt
                 | DeferStmt
                 | SelectStmt
                 | FallThroughStmt
                 | GoStmt'''
    # p[0] = ["Statement", p[1]]
    p[0] = p[1]
    # p[0][0] = "Statement"

def p_fallthrough_stmt(p):
  '''FallThroughStmt : FALLTHROUGH'''
  p[0] = ["FallThroughStmt","fallthrough"]

def p_go_stmt(p):
  '''GoStmt : GO Expression'''
  p[0] = ["GoStmt", "go",p[2]]

# -----------------SELECT STMT --------------------------
def p_select_stmt(p):
  '''SelectStmt : SELECT LCURL CCX RCURL
                | SELECT LCURL RCURL'''
  if len(p) == 5:
    p[0] = ["SelectStmt","select","{",p[3],"}"]
  else:
    p[0] = ["SelectStmt","select","{","}"]

def p_ccx(p):
  '''CCX : CommClause
         | CCX CommClause'''
  if len(p) == 2:
    p[0]=p[1]
  else:
    p[0] = ["CCX",p[1],p[2]]

def p_commclause(p):
  '''CommClause : CommCase COLON StatementList'''
  p[0] = ["CommClause",p[1],":",p[3]]

def p_commcase(p):
  '''CommCase : CASE SendStmt DEFAULT
              | CASE RecvStmt DEFAULT'''
  p[0] = ["CommCase","case",p[1],"default"]

def p_send_stmt(p):
  '''SendStmt : Channel LEFT_ARROW Expression'''
  p[0] = ["SendStmt",p[1],"<-",p[3]]

def p_channel(p):
  '''Channel : Expression'''
  p[0]=p[1]

def p_recv_stmt(p):
  '''RecvStmt : ExpressionList EQUALS RecvExpr
              | IdentifierList SHORT_ASSIGNMENT RecvExpr'''
  if p[2] == "=":
    p[0] = ["RecvStmt",p[1],"=",p[3]]
  elif p[2] == ":=":
    p[0] = ["RecvStmt",p[1],":=",p[3]]

def p_recv_expr(p):
  '''RecvExpr : Expression'''
  p[0]=p[1]

# --------------------------------

def p_defer_stmt(p):
  '''DeferStmt : DEFER Expression'''
  p[0] = ["DeferStmt","defer",p[2]]


def p_simple_stmt(p):
  ''' SimpleStmt : epsilon
                 | ExpressionStmt
                 | IncDecStmt
                 | Assignment
                 | ShortVarDecl '''
  # p[0] = ["SimpleStmt", p[1]]
  p[0] = p[1]
  # p[0][0] = "SimpleStmt"


def p_labeled_statements(p):
  ''' LabeledStmt : Label COLON Statement '''
  p[0] = ["LabeledStmt", p[1], ":", p[3]]

def p_label(p):
  ''' Label : IDENTIFIER '''
  p[0]=p[1]


def p_expression_stmt(p):
  ''' ExpressionStmt : Expression '''
  # p[0] = ["ExpressionStmt", p[1]]
  p[0]=p[1]
  p[0][0] = "ExpressionStmt"

def p_inc_dec(p):
  ''' IncDecStmt : Expression INCREMENT
                 | Expression DECREMENT '''
  if p[2] == '++':
    p[0] = ["IncDecStmt", p[1], "++"]
  else:
    p[0] = ["IncDecStmt", p[1], "--"]


def p_assignment(p):
  ''' Assignment : ExpressionList assign_op ExpressionList'''
  p[0] = [str(p[2]), p[1], p[3]]

def p_assign_op(p):
  ''' assign_op : AssignOp'''
  # p[0] = ["assign_op", p[1]]
  p[0] = p[1]
  # p[0][0] = "assign_op"

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
  # p[0] = ["AssignOp", p[1]]
  p[0] = p[1]
  # p[0][0] = "AssignOp"


def p_if_statement(p):
  ''' IfStmt : IF Expression Block ElseOpt '''
  p[0] = ["IfStmt", "if", p[2], p[3], p[4]]

# def p_SimpleStmtOpt(p):
#   ''' SimpleStmtOpt : SimpleStmt SEMICOLON
#                     | epsilon '''
#   if len(p) == 3:
#     p[0] = ["SimpleStmtOpt", p[1], ";"]
#   else :
#     p[0] = ["SimpleStmtOpt", p[1]]

def p_else_opt(p):
  ''' ElseOpt : ELSE IfStmt
              | ELSE Block
              | epsilon '''
  if len(p) == 3:
    p[0] = ["ElseOpt", "else", p[2]]
  else:
    # p[0] = ["ElseOpt", p[1]]
    p[0]=p[1]

# ----------------------------------------------------------------




def p_switch_statement(p):
  ''' SwitchStmt : ExprSwitchStmt'''
  # p[0] = ["SwitchStmt", p[1]]
  p[0] = p[1]
  p[0][0] = "SwitchStmt"

def p_ExprSwitchStmt(p):
    '''ExprSwitchStmt : SWITCH SimpleStmt SEMICOLON  ExpressionOpt LCURL ExprCaseClauseList RCURL
                 | SWITCH ExpressionOpt LCURL ExprCaseClauseList RCURL '''
    if len(p) == 8:
        p[0] = ["ExprSwitchStmt","switch",p[2],";",p[4],"{",p[6],"}"]
    else:
        p[0] = ["ExprSwitchStmt","switch",p[2],"{",p[4],"}"]


def p_ExprCaseClauseList(p):
    '''ExprCaseClauseList : epsilon
                 | ExprCaseClauseList ExprCaseClause
    '''
    if len(p) == 2:
        p[0]=p[1]
    else:
        p[0] = ["ExprCaseClauseList",p[1],p[2]]

def p_ExprCaseClause(p):
    '''ExprCaseClause : ExprSwitchCase COLON StatementList 
    '''
    p[0] = [":",p[1],p[3]]

def p_ExprSwitchCase(p):
    '''ExprSwitchCase : CASE ExpressionList
                 | DEFAULT 
    '''
    if len(p) == 3:
        p[0] = ["ExprSwitchCase","case",p[2]]
    else:
        p[0] = p[1]
    

# -----------------------------------------------------------



# --------- FOR STATEMENTS AND OTHERS (MANDAL) ---------------
def p_for(p):
  '''ForStmt : FOR ConditionBlockOpt Block'''
  p[0] = ["ForStmt", "for", p[2], p[3]]

def p_conditionblockopt(p):
  '''ConditionBlockOpt : epsilon
             | Condition
             | ForClause
             | RangeClause'''
  # p[0] = ["ConditionBlockOpt", p[1]]
  p[0] = p[1]

def p_condition(p):
  '''Condition : Expression '''
  p[0]=p[1]

def p_forclause(p):
  '''ForClause : SimpleStmt SEMICOLON ConditionOpt SEMICOLON SimpleStmt'''
  p[0] = ["ForClause", p[1], ";", p[3], ";", p[5]]



def p_conditionopt(p):
  '''ConditionOpt : epsilon
          | Condition '''
  # p[0] = ["ConditionOpt", p[1]]
  p[0] = p[1]


def p_rageclause(p):
  '''RangeClause : ExpressionIdentListOpt RANGE Expression'''
  p[0] = ["RangeClause", p[1], "range", p[3]]

def p_expression_ident_listopt(p):
  '''ExpressionIdentListOpt : epsilon
             | ExpressionIdentifier'''
  # p[0] = ["ExpressionIdentListOpt", p[1]]
  p[0] = p[1]

def p_expressionidentifier(p):
  '''ExpressionIdentifier : ExpressionList EQUALS'''
  if p[2] == "=":
    p[0] = ["ExpressionIdentifier", p[1], "="]
  else:
    p[0] = ["ExpressionIdentifier", p[1], ":="]

def p_return(p):
  '''ReturnStmt : RETURN ExpressionListPureOpt'''
  p[0] = ["ReturnStmt", "return", p[2]]

def p_expressionlist_pure_opt(p):
  '''ExpressionListPureOpt : ExpressionList
             | epsilon'''
  # p[0] = ["ExpressionListPureOpt", p[1]]
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
# -----------------------------------------------------------


# ----------------  SOURCE FILE --------------------------------
def p_source_file(p):
    '''SourceFile : PackageClause SEMICOLON ImportDeclRep TopLevelDeclRep'''
    p[0] = ["SourceFile", p[1], ";", p[3], p[4]]

def p_import_decl_rep(p):
  '''ImportDeclRep : epsilon
           | ImportDeclRep ImportDecl SEMICOLON'''
  if len(p) == 4:
    p[0] = ["ImportDeclRep", p[1], p[2], ";"]
  else:
    # p[0] = ["ImportDeclRep", p[1]]
    # p[0] =[]
    p[0] = p[1]

def p_toplevel_decl_rep(p):
  '''TopLevelDeclRep : TopLevelDeclRep TopLevelDecl SEMICOLON
                     | epsilon'''
  if len(p) == 4:
    p[0] = ["TopLevelDeclRep", p[1], p[2], ";"]
  else:
    # p[0] = ["TopLevelDeclRep", p[1]]
    # p[0] =[]
    p[0] = p[1]
# --------------------------------------------------------


# ---------- PACKAGE CLAUSE --------------------
def p_package_clause(p):
    '''PackageClause : PACKAGE PackageName'''
    p[0] = ["PackageClause", "package", p[2]]


def p_package_name(p):
    '''PackageName : IDENTIFIER'''
    # p[0] = ["PackageName", p[1]]
    p[0]=p[1]
# -----------------------------------------------


# --------- IMPORT DECLARATIONS ---------------
def p_import_decl(p):
  '''ImportDecl : IMPORT ImportSpec
          | IMPORT LPAREN ImportSpecRep RPAREN '''
  if len(p) == 3:
    p[0] = ["ImportDecl", "import", p[2]]
  else:
    p[0] = ["ImportDecl", "import", "(", p[3], ")"]

def p_import_spec_rep(p):
  ''' ImportSpecRep : ImportSpecRep ImportSpec SEMICOLON
            | epsilon '''
  if len(p) == 4:
    p[0] = ["ImportSpecRep", p[1], p[2], ";"]
  else:
    # p[0] = ["ImportSpecRep", p[1]]
    p[0] = p[1]

def p_import_spec(p):
  ''' ImportSpec : PackageNameDotOpt ImportPath '''
  if len(p[1]) == 0 :
    p[0]=p[2]
  else:
    p[0] = ["ImportSpec", p[1], p[2]]

def p_package_name_dot_opt(p):
  ''' PackageNameDotOpt : DOT
                        | PackageName
                        | epsilon'''
  if p[1]== '.':
    p[0] = ["PackageNameDotOpt", "."]
  # elif p[1] == "epsilon":
  #   p[0] = []
  else:
    # p[0] = ["PackageNameDotOpt", p[1]]
    p[0] = p[1]

def p_import_path(p):
  ''' ImportPath : STRING_LIT '''
  # p[0] = ["ImportPath", p[1]]
  p[0]=p[1]
# -------------------------------------------------------


def p_empty(p):
  '''epsilon : '''
  # p[0] = "epsilon"
  p[0] = []
  # p[0] = p[1]


# Error rule for syntax errors


# def p_error(p):
#   # print("Syntax error in input!")
#   # print(p)

def p_error(p):
    if p:
      print("Syntax error at line no:", (p.lineno-13), "at position", p.lexpos, "in the code.   " "TOKEN VALUE=", p.value,  "TOKEN TYPE=" ,p.type)
      # print("\n")
      parser.errok()
    else:
      print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()


try:
  s = data
  # print(s)
except EOFError:
  print("khatam bc")
if not s:
  print("bas kar")
result = parser.parse(s,debug=0)

print "Parsing Done ----------------------------> :)"


# new_file_name = file_name.split("/")[-1].split(".")[0] + ".dot"
fname = out_name
sys.stdout =  open(fname, "w+")
######### function to traverse the list of lists ----------------

counter = "global"
counter = 1



def writeGraph(someList):
    global counter
    local=counter
    counter+=1
    name=someList[0]

    if(len(someList) > 1):
        # print str(local)+" [label=\""+name+"\"] ;"
        # for innerList in someList[1:]:
        for i in range(1,len(someList)):
            innerList = someList[i]
            # print "-- name = "+name
            # if name == "PackageClause":
            #     print "------> "+innerList[0]
            #     print "------------------"
            if len(innerList) >0 and type(innerList) is list:
                # print str(local)+" [label=\""+name+"\"] ;"
                print str(counter)+" [label=\"",
                if type(innerList[0]) is list:
                    naming = innerList[0][0]
                else:
                    naming = innerList[0]
                print naming.replace('\"','')+"\" ] ;"
                print str(local) + "->" + str(counter) + ";"
                writeGraph(innerList)
            else:
                if len(innerList) == 0:
                    continue
                # print str(local)+" [label=\""+name+"\"] ;"
                print str(counter)+" [label=\""+innerList.replace('\"','')+"\" ] ;"
                print str(local) + "->" + str(counter) + ";"
            counter+=1

            


############# -----------------------------------------------------
print "digraph G{"
print "1 [label=\"start\"]"
writeGraph(result)
print "}"



#  ^[^#]\s*p\[0\]\ \=\ \["[a-zA-z]*",\s*p\[1\]\s*\]
