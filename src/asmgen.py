from parser import Symbol_Table, Code

# print Code

# print Symbol_Table[0].symbols

asmCode = []
globalDecl = []
global_extra = ['package','import','func','struct','*struct']

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

print_list(globalDecl)