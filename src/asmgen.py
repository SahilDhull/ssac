from parser import Symbol_Table, Code

# print Code

# print Symbol_Table[0].symbols

asmCode = []
globalDecl = []
global_extra = ['package','import','func','struct','*struct']

# Registers:----------------------------------

class Registers(object):
	def __init__(self):
		self.tempRegs = ['$8', '$9', '$10', '$11', '$12', '$13', '$14', '$15']
		self.saveRegs = ['$16', '$17', '$18', '$19', '$20', '$21', '$22', '$23']
		self.regs = self.tempRegs + self.saveRegs
		self.regsState = dict((elem, 0) for elem in self.regs)
		self.lastUsed = dict((elem, -1) for elem in self.regs)

	def free_reg(self):
		for i in self.regs:
			if self.regsState[i]==0:
				return i
		# INCOMPLETE

	def set_reg(self,regval,val):
		self.regsState[regval] = 1
		# INCOMPLETE


	def get_reg(self,val):
		freereg = free_reg()
		set_reg(freereg,1)
		# INCOMPLETE



# ---------------------------------------------

def print_list(l):
  for i in l:
    print i

def global_variables():
	global_sym_tab = Symbol_Table[0]
	globalDecl.append('.data')
	for j in global_sym_tab.symbols:
		sym = global_sym_tab.table[j]
		t = sym.type
		s = sym.mysize
		if t not in global_extra:
			if t.startswith('type'):
				continue;
			# Check if declared or not from 3AC
			globalDecl.append(j+":\t.space "+str(s))

global_variables()

# print_list(globalDecl)

# Start of MIPS
asmCode.append('.globl main')
asmCode.append('.text')
asmCode.append('main:')

def gen_assembly(line):
	destReg = '$r8'
	# get temporary reg

	if line[0]=='=':
		if line[1].startswith('temp_c'):
			asmCode.append('li '+destReg+' '+line[2])
		else:
			asmCode.append('move')

for i in range(len(Code)):
	gen_assembly(Code[i])

print_list(asmCode)