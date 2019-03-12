#!/usr/bin/env python2
from symbol import *

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

