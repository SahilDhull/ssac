class tim:
	def __init__(self):
		self.min = None
		self.sec = None
	def setmin(self,value):
		self.min = value
class other:
	def __init__(self):
		self.table={}
	def setm(self):
		(self.table)["aaa"] = tim()
		(self.table)["aaa"].sec=10
	def printst(self):
		print(self.table["aaa"].sec)

t = other()
x =tim()
t.setm()
t.printst()
a = 5
if(hasattr(x ,'sec')):
	print("ok")
else:
	print("mooo")
if(hasattr(a ,'min')):
	print("ok")
