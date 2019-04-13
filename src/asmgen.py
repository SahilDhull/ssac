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
	# print "-------------------------------------------"
	# print regsState
	for i in regs:
		if regsState[i]==0:
			return i
	return -1

def no_of_free_regs():
	cnt=0
	for i in regs:
		if regsState[i]==0:
			cnt += 1
	return cnt

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

	if var in varToreg and regsState[varToreg[var]]==1:
		return varToreg[var]

	freereg = free_reg()

	if type(freereg) is str:
		varToreg[var] = freereg
		regTovar[freereg] = var
		regsState[freereg] = 1
		if load==0:
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
	global rnum
	rnum = 0
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
	globalDecl.append("str: .asciiz '-----\n' ")
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
eqop = ['=','+=','-=','*=','/=','%=','<<=','>>=',':=','!']  
op = binaryop + eqop

# Start of MIPS
asmCode.append('.data')
asmCode.append("\tstr1: .asciiz \"----\\n\" ")
global_variables()
asmCode.append('.text')
asmCode.append('.globl main')


def gen_assembly(line):
	test = line[0]

	# If Statement
	if test=='ifgoto':
		free_all_reg()
		dest = get_reg(line[1])
		asmCode.append('beq '+dest+', $0, '+line[2])       

	# Label
	if test == 'label':
		if line[1]=='main':
			asmCode.append(line[1]+':')
			asmCode.append('addi $fp, $sp, 0')
		else:
			free_all_reg()
			asmCode.append(line[1]+':')
		# free_all_reg()

	# goto
	if test == 'goto':
		free_all_reg()
		asmCode.append('j '+line[1])

	# Print Statement except string
	if test.startswith('print'):
		arg1 = line[1]
		if arg1.startswith('addr_'):
			arg1 = arg1[5:]
			reg1 = get_reg(arg1)
			asmCode.append('lw $4, '+'0('+reg1+')')
			asmCode.append('li $2, 1')
			asmCode.append('syscall')
			return
		
		if len(test)==9: #print int
			src = get_reg(line[1])
			asmCode.append('li $2, 1')
			asmCode.append('move $4, '+src)
			asmCode.append('syscall')
		elif len(test)==11: # print float
			src = get_reg(line[1])
			asmCode.append('li $2, 2')
			asmCode.append('move $f12, '+src)
			asmCode.append('syscall')
		else:       # string case
			asmCode.append('Print String not Implemented')

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

	if test == 'mem+':
		src = get_reg(line[1])
		asmCode.append('add '+src+', '+src+', '+line[2])



	if test=='$sp':
		asmCode.append('addi $sp, $sp, '+line[1])

	if test=='loadra':
		asmCode.append('lw $ra, '+line[2])

	if test == 'jr':
		free_all_reg()
		funcinfo = findinfo(line[2])
		asmCode.append('addi $sp, $sp, '+str(-funcinfo.funcsize))
		asmCode.append('jr $ra')

	if test == 'jret':
		free_all_reg()
		funcinfo = findinfo(line[2])
		asmCode.append('addi $sp, $sp, '+str(-funcinfo.funcsize))
		asmCode.append('jr $ra')
		asmCode.append('addi $sp, $sp, '+str(funcinfo.funcsize))

	if test =='movs':
		src = get_reg(line[1])
		asmCode.append('sw '+src+', '+line[2])

	if test == 'jal':
		# free_all_reg()
		asmCode.append('jal '+line[1])

	if test=='addi':
		if line[1]=='$fp':
			free_all_reg()
		asmCode.append('addi '+line[1]+', '+line[2]+', '+line[3])

	if test=='memt':
		size = int(line[3])
		off = int(line[1])
		arg = line[2]
		free_all_reg()
		src = free_reg()
		info = findinfo(arg)
		varoff = info.offset
		while size:
			asmCode.append('lw '+src+', '+str(off)+'($fp)')
			asmCode.append('sw '+src+', '+str(varoff)+'($fp)')
			varoff += 4
			off += 4
			size -=4

	if test == 'push':
		if line[1] == '$ra':
			asmCode.append('sw $ra, '+line[2]+'($fp)')
		elif (line[1]).lstrip('-+').isdigit():
			asmCode.append('li $3, '+line[1])
			asmCode.append('sw $3, '+line[2]+'($fp)')
		else:
			arg1 = line[1]
			arg2 = int(line[2])
			arg3 = int(line[3])
			free_all_reg()
			src = free_reg()
			info = findinfo(arg1)
			off = info.offset
			num = arg2
			while num:
				asmCode.append('lw '+src+', '+str(off)+'($fp)')
				asmCode.append('sw '+src+', '+str(arg3)+'($fp)')
				arg3 += 4
				off += 4
				num -= 4

	if test == '++':
		reg = get_reg(line[1])
		info = findinfo(line[1])
		asmCode.append('addi '+reg+', 1')
		asmCode.append('sw '+reg+', '+str(info.offset)+'($fp)')

	if line[0] in eqop:
		arg1 = str(line[1])
		arg2 = str(line[2])
		flag = 0

		if line[0]=='=' and arg1.startswith('temp_c'):
			dest = get_reg(line[1])
			if line[2]=='true':
				asmCode.append('li '+dest+', 0x1')
			elif line[2]=='false':
				asmCode.append('li '+dest+', 0x0')
			else:
				asmCode.append('li '+dest+', '+str(line[2]))
			return

		if arg1.startswith('addr_') and arg2.startswith('addr_'):
			if no_of_free_regs()<4:
				free_all_reg()
			arg1 = arg1[5:]
			arg2 = arg2[5:]
			reg1 = get_reg(arg1)
			reg2 = get_reg(arg2)
			flag = 1
			cnt = 2

			for reg in regs:
				if cnt == 0:
					break
				if reg != reg1 and reg != reg2 and cnt == 2:
					empty_reg(reg)
					src1 = reg
					cnt -= 1
					continue
				if reg != reg1 and reg != reg2 and cnt == 1:
					empty_reg(reg)
					dest = reg
					cnt -= 1
					continue
			asmCode.append('lw '+dest+', 0('+reg1+')')
			asmCode.append('lw '+src1+', 0('+reg2+')')

		elif arg1.startswith('addr_'):
			if no_of_free_regs()<3:
				free_all_reg()
			flag = 2
			arg1 = arg1[5:]
			reg1 = get_reg(arg1)
			src1 = get_reg(arg2)

			for reg in regs:
				if reg != reg1 and reg != src1:
					empty_reg(reg)
					dest = reg
					break
			asmCode.append('lw '+dest+', 0('+reg1+')')

		elif arg2.startswith('addr_'):
			if no_of_free_regs()<3:
				free_all_reg()
			flag = 3
			arg2 = arg2[5:]
			reg2 = get_reg(arg2)
			dest = get_reg(arg1)

			for reg in regs:
				if reg != reg2 and reg != dest:
					empty_reg(reg)
					src1 = reg
					break
			asmCode.append('lw '+src1+', 0('+reg2+')')

		else:
			dest = get_reg(arg1)
			src1 = get_reg(arg2)

		
		x = line[0]
		info1 = findinfo(arg1)
		typ1 = info1.type
		info2 = findinfo(arg2)
		typ2 = info2.type


		if line[0]=='=' and (typ1=='float' or typ1=='int' or typ1=='bool' or typ2=='float' or typ2=='int' or typ2=='bool' or typ1 == None or typ2 == None):
			asmCode.append('move '+dest+', '+src1)
		elif x=='=':
			siz = info1.mysize
			off1 = info1.offset
			off2 = info2.offset
			free_all_reg()
			regn = free_reg()
			while siz:
				asmCode.append('lw '+regn+', '+str(off2)+'($fp)')
				asmCode.append('sw '+regn+', '+str(off1)+'($fp)')
				off1 += 4
				off2 += 4
				siz -= 4
				

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
			asmCode.append('seq ' + dest + ', ' + src1+', $0')

		if flag == 1 or flag == 2:
			asmCode.append('sw '+dest+', 0('+reg1+')')
		return 1
		
		
	if line[0] in binaryop:
		arg0 = str(line[1])
		arg1 = str(line[2])
		arg2 = str(line[3])
		flag = 0
		# free_all_reg()
		if no_of_free_regs()<6:
			free_all_reg()

		if arg0.startswith('addr_'):
			flag = 1
			reg1 = get_reg(arg1[5:])
			dest = free_reg()
			regsState[dest] = 1
			asmCode.append('lw '+dest+', 0('+reg1+')')
		else:
			dest = get_reg(arg0)

		if arg1.startswith('addr_'):
			reg2 = get_reg(arg1[5:])
			src1 = free_reg()
			regsState[src1] = 1
			asmCode.append('lw '+src1+', 0('+reg2+')')
		else:
			src1 = get_reg(arg1)

		if arg2.startswith('addr_'):
			reg3 = get_reg(arg2[5:])
			src2 = free_reg()
			regsState[src2] = 1
			asmCode.append('lw '+src2+', 0('+reg3+')')
		else:
			src2 = get_reg(arg2)
		
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

		if flag:
			asmCode.append('sw '+dest+', 0('+reg1+')')

		return 1


# Updating symbol table
update_symbol_table()	


for i in range(len(Code)):
	gen_assembly(Code[i])

for i in range(len(asmCode)):
	line = asmCode[i]
	if line.endswith(':') or line.startswith('.'):
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