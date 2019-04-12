#!/usr/bin/env python2

class symnode:
	def __init__(self):
		self.name = None
		self.type = None
		self.retType = []
		self.retsize = []
		self.label = None
		self.listsize = None
		self.place = None
		self.child = None
		self.offset = None
		self.mysize = 0
		self.funcsize = 0

	def insertname(self,name):
		self.name = name

	def insertType(self,type1):
		self.type = type1

	def insertretType(self,a):
		self.retType += [a]

	def insertlabel(self,a):
		self.label = a

	def insertlistsize(self,a):
		self.listsize = a

	def insertplace(self,a):
		self.place = a

	def insertchild(self,a):
		self.child = a

	def insertoffset(self,a):
		self.offset = a

	def insertmysize(self,a):
		self.mysize = a

class st:
	def __init__(self,val):
		self.val = val
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

	def insert(self,name,type1,m=None):
		if(not self.look(name)):
			(self.table)[name] = symnode()
			self.symbols.append(name)
			(self.table)[name].insertType(type1)
			(self.table)[name].insertname(m)

	def retrieve(self,name):
		if(self.look(name)):
			return (self.table)[name]
		return None

	def updateAttr(self,name,s,val):
		if(self.look(name)):
			if(s=="type"):
				(self.table)[name].insertType(val)
			elif(s=="ret"):
				(self.table)[name].insertretType(val)
			elif(s=="label"):
				(self.table)[name].insertlabel(val)
			elif(s=="size"):
				(self.table)[name].insertlistsize(val)
			elif(s=="place"):
				(self.table)[name].insertplace(val)
			elif(s=="child"):
				(self.table)[name].insertchild(val)
			elif(s=="offset"):
				(self.table)[name].insertoffset(val)
			elif(s=="mysize"):
				(self.table)[name].insertmysize(val)
			# else:
			# 	(self.table)[name].insertextra(val)
		else:
			raise Error(name+"isn't found")

class node:
	def __init__(self):
		self.idlist=[]
		self.code=[]
		self.types=[]
		self.place=[]
		self.size=[]
		self.limits=[]
		self.bytesize = 0
		self.extra={}
		self.retsize=[]