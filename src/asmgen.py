from parser import Symbol_Table, Code, scopeStack, findinfo

# print Code

# print Symbol_Table[0].symbols

asmCode = []
globalDecl = []
global_extra = ['package','import','func','struct','*struct']


def findscope(name):
	for s in scopeStack[::-1]:
		if Symbol_Table[s].retrieve(name) is not None:
			return s
	return -1

def off_cal(varname):
	s = findscope(varname)
	if s==-1:
		print "Some Error"
	info = findinfo(varname,s)
	off = info.offset
	return -4-off

# Registers:----------------------------------

regs = ["$r"+str(i) for i in range(2,26)]
regsState = dict((i, 0) for i in regs)
rnum = 0
regTovar = {}
varToreg = {}

def free_reg():
	for i in regs:
		if regsState[i]==0:
			return i
	return -1

def get_reg():
	freereg = free_reg()
	if freereg != -1:
		regsState[freereg] = 1
		return freereg
	global rnum
	reg_to_rep = regs[rnum%len(regs)]
	rnum += 1
	varname = regTovar[reg_to_rep]
	off = off_cal(varname)
	asmCode.append('sw '+reg_to_rep+', '+str(off)+'($fp)')
	return reg_to_rep

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
	# src1 = get_reg()
	# src2 = get_reg()
	# get temporary reg

	if line[0]=='=':
		if line[1].startswith('temp_c'):
			dest = get_reg()
			asmCode.append('li '+dest+', '+line[2])
		else:
			asmCode.append('move')

for i in range(len(Code)):
	gen_assembly(Code[i])

print_list(asmCode)