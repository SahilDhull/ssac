#!/usr/bin/env python2
from symbol import *

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


def definedcheck(name):
  # print "here ==========> "+name
  # print scopeStack
  for scope in scopeStack[::-1]:
    # print scopeDict[scope].table
    if scopeDict[scope].retrieve(name) is not None:
      return True
  return False