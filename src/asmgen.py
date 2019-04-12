from parser import Symbol_Table, Code
import sys

asmCode = []
globalDecl = []
global_extra = ['package','import','func','struct','*struct']

def print_list(l):
	for i in l:
		print i

def print_Symbol_Table():
	for i in range(len(Symbol_Table)):
		print "Symbol_Table["+str(i)+"] :"
		print Symbol_Table[i].__dict__
		print ""

# print_Symbol_Table()

def findscope(name):
	for j in range(len(Symbol_Table)):
		i = Symbol_Table[j]
		if name in i.symbols:
			return j
	return -1

def findinfo(name):
	S = findscope(name)
	if Symbol_Table[S].retrieve(name) is not None:
		return Symbol_Table[S].retrieve(name)
	print "Identifier " + name + " is not defined!"

def off_cal(varname):
	info = findinfo(varname)
	off = info.offset
	return off

def update_symbol_table():
	for j in range(len(Symbol_Table)):
		i = Symbol_Table[j]
		for x in range(len(i.symbols)):
			symbol = i.symbols[x]
			sym = i.table[i.symbols[x]]
			if sym.place is not None:
				# print sym.place
				i.symbols[x] = sym.place
				i.table[sym.place] = sym
				del i.table[symbol]

# Registers:----------------------------------

regs = ["$"+str(i) for i in range(5,26)]
regsState = dict((i, 0) for i in regs)
rnum = 0
regTovar = {}
varToreg = {}

def free_reg():
	for i in regs:
		if regsState[i]==0:
			return i
	return -1

def reg_replace(reg_to_rep,newVar=None):
	oldVar = regTovar[reg_to_rep]
	old_off = off_cal(oldVar)
	asmCode.append('sw '+reg_to_rep+', '+str(old_off)+'($fp)')
	if newVar:
		regTovar[reg_to_rep] = newVar
		varToreg[newVar] = reg_to_rep
		off = off_cal(newVar)
		asmCode.append('lw '+reg_to_rep+', '+str(off)+'($fp)')

def get_reg(var,load=0):
	info = findinfo(var)
	off = off_cal(var)
	c = 0

	if var.startswith('off_'):
		num = [int(s) for s in (line[2]).split() if s.isdigit()]
		o = str(- 4 - num[0])
		return o+"($fp)"

	if var.startswith('temp_c'):
		c = 1

	if var in varToreg and regsState[varToreg[var]]==1:
		return varToreg[var]

	freereg = free_reg()

	if freereg != -1:
		varToreg[var] = freereg
		regTovar[freereg] = var
		regsState[freereg] = 1
		if c==0 and load==0:
			asmCode.append('lw '+freereg+', '+str(off)+'($fp)')
		return freereg
	global rnum
	reg_to_rep = regs[rnum%len(regs)]
	rnum += 1
	varname = regTovar[reg_to_rep]
	reg_replace(reg_to_rep,varname)
	return reg_to_rep

def empty_reg(reg):
	if regsState[reg] == 0:
		return
	regsState[reg] = 0
	if reg not in regTovar:
		return
	varname = regTovar[reg]
	old_off = off_cal(varname)
	asmCode.append('sw '+reg+', '+str(old_off)+'($fp)')
	del regTovar[reg]
	del varToreg[varname]

def free_all_reg():
	for i in range(len(regs)):
		reg = regs[i]
		regsState[reg] = 0
		if reg not in regTovar:
			continue
		varname = regTovar[reg]
		old_off = off_cal(varname)
		asmCode.append('sw '+reg+', '+str(old_off)+'($fp)')
		del regTovar[reg]
		del varToreg[varname]


# ---------------------------------------------

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


# print_list(globalDecl)

binaryop = ['+','-','*','/','%','&&','||','^','!=','<=','>=','==','<','>','<<','>>']
eqop = ['+=','-=','*=','/=','%=','<<=','>>=',':=','!']  
op = binaryop + eqop

# Start of MIPS
asmCode.append('.data')
global_variables()
asmCode.append('.text')
asmCode.append('.globl main')


def gen_assembly(line):
	test = line[0]

	# If Statement
	if test=='ifgoto':
		dest = get_reg(line[1])
		asmCode.append('bgtz '+dest+', '+line[2])       

	# Label
	if test == 'label':
		asmCode.append(line[1]+':')
		if line[1]=='main':
			asmCode.append('addi $fp, $sp, 0')

	# goto
	if test == 'goto':
		asmCode.append('j '+line[1])

	# Print Statement except string
	if test.startswith('print'):
		src = get_reg(line[1])
		if len(test)==9: #print int
			asmCode.append('li $2, 1')
			asmCode.append('move $4, '+src)
			asmCode.append('syscall')
		elif len(test)==11: # print float
			asmCode.append('li $2, 2')
			asmCode.append('move $f12, '+src)
			asmCode.append('syscall')
		else:       # string case
			asmCode.append('Print String not Implemented')
		regsState[src] = 0

	if test.startswith('scan'):
		dest = get_reg(line[1])
		if len(test)==8:
			asmCode.append('li $2, 5')
			asmCode.append('syscall')
			asmCode.append('move '+dest+', $2')
		elif len(test) == 11:
			asmCode.append('li $2, 6')
			asmCode.append('syscall')
			asmCode.append('move '+dest+', $f0')
		else:
			asmCode.append('Scan string not Implemented')

	if test=='memt':
		src = get_reg(line[2],1)
		offset = off_cal(line[2])
		asmCode.append('lw '+src+', '+line[1])
		asmCode.append('sw '+src+', '+str(offset)+'($fp)')

	if test=='$sp':
		asmCode.append('addi $sp, $sp, '+line[1])

	if test=='loadra':
		asmCode.append('lw $ra, '+line[2])

	if test == 'jr':
		asmCode.append(line[0]+' '+line[1])

	if test =='movs':
		src = get_reg(line[1])
		asmCode.append('sw '+src+', '+line[2])

	if test == 'jal':
		asmCode.append('jal '+line[1])

	if test=='addi':
		asmCode.append('addi '+line[1]+', '+line[2]+', '+line[3])

	if test == 'push':
		if line[1] == '$ra':
			asmCode.append('sw $ra, '+line[2]+'($fp)')
		elif (line[1]).lstrip('-+').isdigit():
			asmCode.append('li $3, '+line[1])
			asmCode.append('sw $3, '+line[2]+'($fp)')
		else:
			src = get_reg(line[1])
			asmCode.append('sw '+src+', '+line[3]+'($fp)')

	if line[0]=='=':
		if line[1].startswith('temp_c'):
			dest = get_reg(line[1])
			asmCode.append('li '+dest+', '+line[2])
		
		elif line[2].startswith('off_'):
			src = get_reg(line[2])
			dest = get_reg(line[1])
			asmCode.append('lw ' + dest + ', ' + src)
		else:
			src = get_reg(line[2])
			dest = get_reg(line[1],1)
			asmCode.append('move '+dest+', '+src)
	
	if line[0] in eqop:
		dest = get_reg(line[1])
		src1 = get_reg(line[2])
		x = line[0]
		
		if (x == '+='):
			asmCode.append('add ' + dest + ', ' + dest + ', ' + src1)
		
		if (x == '-='):
			asmCode.append('sub ' + dest + ', ' + dest + ', ' + src1)
		
		if (x == '*='):
			asmCode.append('mult ' + dest + ', ' + src1)
			asmCode.append('mflo ' + dest)
		
		if (x == '/='):
			asmCode.append('div ' + dest + ', ' + src1)
			asmCode.append('mflo ' + dest)
		
		if (x == '%='):
			asmCode.append('div ' + dest + ', ' + src1)
			asmCode.append('mfhi ' + dest)
		
		if (x == '<<='):
			asmCode.append('sllv ' + dest + ', ' + dest + ', ' + src1)
		
		if (x == '>>='):
			asmCode.append('srlv ' + dest + ', ' + dest + ', ' + src1)
		
		if (x == ':='):
			asmCode.append('move ' + dest + ', ' + src1)

		if x == '!':
			asmCode.append('nor ' + dest + ', ' + src1 + ', $0')
			
		regsState[src1] = 0
		return 1
		
		
	if line[0] in binaryop:
		dest = get_reg(line[1])
		src1 = get_reg(line[2])
		src2 = get_reg(line[3])
		
		x = line[0]
		
		if x == '+':
			asmCode.append('add '+dest+', '+src1+', '+src2)
		
		if x == '-':
			asmCode.append('sub '+dest+', '+src1+', '+src2)
		
		if x == '*':
			asmCode.append('mult '+src1+', '+src2)
			asmCode.append('mflo '+ dest)
		
		if x == '/':
			asmCode.append('div '+src1+', '+src2)
			asmCode.append('mflo ' + dest)
		
		if x == '%':
			asmCode.append('div '+src1+', '+src2)
			asmCode.append('mfhi ' + dest)
		
		if x == '&&':
			asmCode.append('and '+dest+', '+src1+', '+src2)
		
		if x == '||':
			asmCode.append('or '+dest+', '+src1+', '+src2)
		
		if x == '^':
			asmCode.append('xor '+dest+', '+src1+', '+src2)
		
		if x == '!=':
			asmCode.append('sne '+dest+', '+src1+', '+src2)
		
		if x == '<=':
			asmCode.append('sle '+dest+', '+src1+', '+src2)
		
		if x == '>=':
			asmCode.append('sge '+dest+', '+src1+', '+src2)
		
		if x == '==':
			asmCode.append('seq '+dest+', '+src1+', '+src2)
			
		if x == '<':
			asmCode.append('slt '+dest+', '+src1+', '+src2)
			
		if x == '>':
			asmCode.append('sgt '+dest+', '+src1+', '+src2)
		
		if x == '<<':
			asmCode.append('sllv '+dest+', '+src1+', '+src2)
		
		if x == '>>':
			asmCode.append('srlv '+dest+', '+src1+', '+src2)
		
		if src1!= dest:
			regsState[src1] = 0
		regsState[src2] = 0
		return 1


# Updating symbol table
update_symbol_table()	


for i in range(len(Code)):
	gen_assembly(Code[i])

for i in range(len(asmCode)):
	line = asmCode[i]
	if line.endswith(':'):
		continue
	else:
		asmCode[i] = '\t'+line

# free_all_reg()

sys.stdout =  open("mips", "w+")

# print_Symbol_Table()

print_list(asmCode)

# ----------- To remove on function implementation
"""
print "li $v0, 1"
print "move $a0, $3"
print "syscall"

print "li $v0, 10"
print "syscall"
"""
# ----------------