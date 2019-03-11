#!/usr/bin/env python2

class symnode:
	def __init__(self):
		self.type = None
		self.retType = None
		self.label = None
		self.listsize = None
		self.place = None
		self.child = None

	def insertType(self,type1):
		self.type = type1

	def insertretType(self,a):
		self.retType = a

	def insertlabel(self,a):
		self.label = a

	def insertlistsize(self,a):
		self.listsize = a

	def insertplace(self,a):
		self.place = a

	def insertchild(self,a):
		self.child = a

class st:
	def __init__(self):
		self.table = {}
		self.symbols = []
		self.parent = None
		self.extra = {}

	def setParent(self,p):
		self.parent = p

	def updateExtra(self,s,value):
		self.extra[s]=value

	def look(self,name):
		return (name in self.table)

	def insert(self,name,type1):
		if(not self.look(name)):
			(self.table)[name] = symnode()
			self.symbols.append(name)
			(self.table)[name].insertType(type1)

	def retrieve(self,name):
		if(self.look(name)):
			return (self.table)[name]
		return None

	def updateAttr(self,name,s,val):
		if(self.look(name)):
			if(s=="type"):
				(self.table)[name].insertType(val)
			if(s=="ret"):
				(self.table)[name].insertretType(val)
			if(s=="label"):
				(self.table)[name].insertlabel(val)
			if(s=="size"):
				(self.table)[name].insertlistsize(val)
			if(s=="place"):
				(self.table)[name].insertplace(val)
			if(s=="child"):
				(self.table)[name].insertchild(val)
		else:
			raise Error(name+"isn't found")

class node:
	def __init__(self):
		self.idlist=[]
		self.code=[]
		self.types=[]
		self.place=[]
		self.extra={}