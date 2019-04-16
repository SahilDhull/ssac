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
fregs = ["$f"+str(i) for i in [4,5,6,7,8,9,10,16,17,18,19,20,21,22,23,24,25,26,27,28,29]]
regsState = dict((i, 0) for i in regs)
floatState = dict((i,0) for i in fregs)
fnum = 0
rnum = 0
regTovar = {}
varToreg = {}
regTofloat = {}
floatToreg = {}

def free_reg():
	# print "-------------------------------------------"
	# print regsState
	for i in regs:
		if regsState[i]==0:
			regsState[i]=1
			return i
	return -1

def free_float():
	for i in fregs:
		if floatState[i]==0:
			floatState[i]=1
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

def float_replace(reg_to_rep,newVar=None):
	oldVar = regTofloat[reg_to_rep]
	old_off = off_cal(oldVar)
	asmCode.append('swc1 '+reg_to_rep+', '+str(old_off)+'($fp)')
	if newVar:
		regTofloat[reg_to_rep] = newVar
		floatToreg[newVar] = reg_to_rep
		off = off_cal(newVar)
		asmCode.append('lwc1 '+reg_to_rep+', '+str(off)+'($fp)')

def get_reg(var,load=0):
	info = findinfo(var)
	off = off_cal(var)
	flag = 0
	if off==None:
		flag = 1

	if var in varToreg and regsState[varToreg[var]]==1:
		return varToreg[var]

	freereg = free_reg()

	if type(freereg) is str:
		varToreg[var] = freereg
		regTovar[freereg] = var
		regsState[freereg] = 1
		if load==0 and flag==0:
			asmCode.append('lw '+freereg+', '+str(off)+'($fp)')
		elif flag == 1:
			asmCode.append('lw '+freereg+', '+str(off)+'($fp)')
		return freereg
	global rnum
	reg_to_rep = regs[rnum%len(regs)]
	rnum += 1
	varname = regTovar[reg_to_rep]
	reg_replace(reg_to_rep,varname)
	return reg_to_rep

def get_float(var, load=0):
	info = findinfo(var)
	off = off_cal(var)
	if var in floatToreg and floatState[floatToreg[var]]==1:
		return floatToreg[var]

	freefloat = free_float()

	if type(freefloat) is str:
		floatToreg[var] = freefloat
		regTofloat[freefloat] = var
		floatState[freefloat] = 1
		if load==0:
			asmCode.append('lwc1 '+freefloat+', '+str(off)+'($fp)')
		return freefloat
	global fnum
	reg_to_rep = fregs[fnum%len(fregs)]
	fnum += 1
	varname = regTofloat[reg_to_rep]
	float_replace(reg_to_rep,varname)
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

def only_empty(reg):
	regsState[reg] = 0
	del varToreg[regTovar[reg]]
	del regTovar[reg]

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

binaryop = ['+','-','*','/','%','&','|','^','!=','<=','>=','==','<','>','<<','>>']
eqop = ['=','+=','-=','*=','/=','%=','<<=','>>=',':=','!']  
op = binaryop + eqop

feqop = ['f=','f+=','f-=','f*=','f/=']
fbop = ['f+','f-','f*','f/']

# Start of MIPS
asmCode.append('.data')
# asmCode.append("\tstr1: .asciiz \"----\\n\" ")
global_variables()
asmCode.append('.text')
asmCode.append('.globl main')


def gen_assembly(line):
	test = line[0]

	if test == 'call_malloc':
		dest = get_reg(line[1])
		asmCode.append('li $a0, '+str(line[2]))
		asmCode.append('li $v0, 9')
		asmCode.append('syscall')
		asmCode.append('move '+dest+', $v0')
		empty_reg(dest)


	# ---------   FLOAT  -------------------
	# To complete
	if test.startswith('f'):
		x = test

		if test=='fprint':
			dest = get_float(line[1])
			asmCode.append('li, $v0, 2')
			asmCode.append('mov.s $f12, '+dest)
			asmCode.append('syscall')

		if test=='fscan':
			asmCode.append('li $2, 6')
			asmCode.append('syscall')

		if test in feqop:
			arg1 = str(line[1])
			arg2 = str(line[2])

			dest = get_float(arg1)

			if x=='f=' and arg1.startswith('temp_c'):
				asmCode.append('li.s '+dest+', '+arg2)
				return

			src = get_float(arg2)		

			if x=='f=':
				asmCode.append('mov.s '+dest+', '+src)
			elif x=='f+=':
				asmCode.append('add.s '+dest+', '+dest+', '+src)
			elif x=='f-=':
				asmCode.append('sub.s '+dest+', '+dest+', '+src)
			elif x=='f*=':
				asmCode.append('mul.s '+dest+', '+dest+', '+src)
			elif x=='f/=':
				asmCode.append('div.s '+dest+', '+dest+', '+src)

		if test in fbop:
			arg1 = str(line[1])
			arg2 = str(line[2])
			arg3 = str(line[3])

			dest = get_float(arg1)
			src1 = get_float(arg2)
			src2 = get_float(arg3)

			if x=='f+':
				asmCode.append('add.s '+dest+', '+src1+', '+src2)
			if x=='f-':
				asmCode.append('sub.s '+dest+', '+src1+', '+src2)
			if x=='f*':
				asmCode.append('mul.s '+dest+', '+src1+', '+src2)
			if x=='f/':
				asmCode.append('div.s '+dest+', '+src1+', '+src2)				

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
		if len(test)==12 and arg1.startswith('addr_'):
			arg1 = arg1[5:]
			reg1 = get_reg(arg1)
			asmCode.append('move $4, '+reg1)
			asmCode.append('li $2, 4')
			asmCode.append('syscall')
			return
		elif len(test) == 12:
			info = findinfo(line[1])
			asmCode.append('li $2, 4')
			asmCode.append('addi $4, $fp, '+str(info.offset))
			asmCode.append('syscall')
			return
		cnt = 0
		if arg1.startswith('addr_'):
			while arg1.startswith('addr_'):
				arg1 = arg1[5:]
				cnt+=1
			reg1 = get_reg(arg1)
			info = findinfo(arg1)
			# print info.mysize
			asmCode.append('move $4, '+reg1)
			while cnt:
				cnt-=1
				asmCode.append('lw $4, 0($4)')
			asmCode.append('li $2, 1')
			asmCode.append('syscall')
			regsState[reg1] = 0
			del varToreg[arg1]
			del regTovar[reg1]
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

	if test.startswith('scan'):
		if test.endswith('int'):
			dest = get_reg(line[1])
			asmCode.append('li $2, 5')
			asmCode.append('syscall')
			asmCode.append('move '+dest+', $2')
		
		elif test.endswith('float'):
			dest = get_reg(line[1])
			asmCode.append('li $2, 6')
			asmCode.append('syscall')
			asmCode.append('move '+dest+', $f0')
		
		elif test.endswith('string'):
			info = findinfo(line[1])
			empty_reg('$5')
			asmCode.append('li $2, 8')
			asmCode.append('li $5, 32')
			asmCode.append('addi $4, $fp, '+str(info.offset))
			asmCode.append('syscall')


	if test == 'addr':
		arg1 = line[1]
		arg2 = line[2]
		dest = get_reg(arg1)
		info = findinfo(arg2)
		off = info.offset
		asmCode.append('add '+dest+', $fp, '+str(off))

	if test == 'load':
		arg1 = line[1]
		arg2 = line[2]
		dest = get_reg(arg1)
		src = get_reg(arg2)
		asmCode.append('lw '+dest+', '+'0('+src+')')

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
			if arg1.startswith('addr_'):
				arg1 = arg1[5:]
				reg1 = get_reg(arg1)
				asmCode.append('lw '+src+', 0('+reg1+')')
				asmCode.append('sw '+src+', '+str(arg3)+'($fp)')
				return
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

		if line[0]=='=' and arg1.startswith('temp_str'):
			arg = str(line[2][1:-1])
			dest = get_reg(arg1)
			info = findinfo(arg1)
			off = info.offset
			info.type = 'string'
			l = len(arg)
			i=0
			cnt = 32
			while i < len(arg) and cnt>1:
				c = arg[i]
				if arg[i]=='\\':
					l-=1
					i+=1
					if arg[i]=='n':
						c = '\n'
					elif arg[i]=='t':
						c = '\t'
					elif arg[i]=='\"':
						c = '\"'
					elif arg[i]=='\'':
						c = '\''
					elif arg[i]=='\\':
						c = '\\'
				cnt-=1
				o = ord(c)
				asmCode.append('li '+dest+', '+str(o))
				asmCode.append('sb '+dest+', '+str(off)+'($fp)')
				i+=1
				off += 1
			while cnt>0:
				asmCode.append('li '+dest+', 0')
				asmCode.append('sb '+dest+', '+str(off)+'($fp)')
				cnt-=1
				off+=1
			# asmCode.append('li '+dest+', '+str(l))
			# asmCode.append('sw '+dest+', '+str(info.offset+28)+'($fp)')
			regsState[dest]=0
			del varToreg[arg1]
			del regTovar[dest]

			return

		if arg1.startswith('addr_') and arg2.startswith('addr_'):
			if no_of_free_regs()<6:
				free_all_reg()
			flag = 1
			# arg1 = arg1[5:]
			# arg2 = arg2[5:]
			cnt1 = 0
			cnt2 = 0
			while arg1.startswith('addr_'):
				arg1 = arg1[5:]
				cnt1+=1
			while arg2.startswith('addr_'):
				arg2 = arg2[5:]
				cnt2+=1
			reg1 = get_reg(arg1)
			reg2 = get_reg(arg2)

			# cnt = 2

			src1 = free_reg()
			dest = free_reg()
			regs1 = free_reg()
			regs2 = free_reg()

			# for reg in regs:
			# 	if cnt == 0:
			# 		break
			# 	if reg != reg1 and reg != reg2 and cnt == 2:
			# 		empty_reg(reg)
			# 		src1 = reg
			# 		cnt -= 1
			# 		continue
			# 	if reg != reg1 and reg != reg2 and cnt == 1:
			# 		empty_reg(reg)
			# 		dest = reg
			# 		cnt -= 1
			# 		continue

			while cnt1>1:
				cnt1-=1
				asmCode.append('lw '+reg1+', 0('+reg1+')')
			asmCode.append('lw '+regs1+', 0('+reg1+')')

			while cnt2>1:
				cnt2-=1
				asmCode.append('lw '+reg2+', 0('+reg2+')')
			asmCode.append('lw '+regs2+', 0('+reg2+')')
			
			asmCode.append('move '+dest+', '+regs1)
			asmCode.append('move '+src1+', '+regs2)
			# only_empty(reg1)
			# only_empty(reg2)
			regsState[regs1] = 0
			regsState[regs2] = 0


		elif arg1.startswith('addr_'):
			if no_of_free_regs()<4:
				free_all_reg()
			flag = 2
			# arg1 = arg1[5:]
			cnt1 = 0
			while arg1.startswith('addr_'):
				arg1 = arg1[5:]
				cnt1+=1

			reg1 = get_reg(arg1)
			src1 = get_reg(arg2)
			dest = free_reg()
			# regs1 = free_reg()

			while cnt1>1:
				cnt1-=1
				asmCode.append('lw '+reg1+', 0('+reg1+')')
			asmCode.append('lw '+dest+', 0('+reg1+')')
			# for reg in regs:
			# 	if reg != reg1 and reg != src1:
			# 		empty_reg(reg)
			# 		dest = reg
			# 		break
			# asmCode.append('move '+dest+', '+regs1)
			# regsState[regs1] = 0

		elif arg2.startswith('addr_'):
			if no_of_free_regs()<3:
				free_all_reg()
			flag = 3
			# arg2 = arg2[5:]
			cnt2 = 0
			while arg2.startswith('addr_'):
				arg2 = arg2[5:]
				cnt2+=1
			reg2 = get_reg(arg2)
			dest = get_reg(arg1)
			src1 = free_reg()
			while cnt2>1:
				cnt2-=1
				asmCode.append('lw '+reg2+', 0('+reg2+')')
			asmCode.append('lw '+src1+', 0('+reg2+')')
			# asmCode.append('move '+src1+', '+regs2)
			# for reg in regs:
			# 	if reg != reg2 and reg != dest:
			# 		empty_reg(reg)
			# 		src1 = reg
			# 		break


		else:
			info1 = findinfo(arg1)
			typ1 = info1.type
			info2 = findinfo(arg2)
			typ2 = info2.type
			if (typ1=='string' or typ2=='string'):
				abcd=1
			# elif (typ1.startswith('*')):

			else:
				dest = get_reg(arg1)
				src1 = get_reg(arg2)

		
		x = line[0]
		info1 = findinfo(arg1)
		typ1 = info1.type
		info2 = findinfo(arg2)
		typ2 = info2.type

		if line[0] == '=' and (info1.mysize==4 and info2.mysize==4) and (flag != 1):
		# if line[0]=='=' and (typ1.startswith('*') or typ2.startswith('*') or typ1=='float' or typ1=='int' or typ1=='bool' or typ2=='float' or typ2=='int' or typ2=='bool' or (typ1 == None and typ2 == None)):

			asmCode.append('move '+dest+', '+src1)
			empty_reg(dest)
			empty_reg(src1)
			# empty_reg(dest)
		
##################################################################
		# elif x=='=':
		# 	print "aa gya"
		# 	siz = info1.mysize
		# 	off1 = info1.offset
		# 	off2 = info2.offset
		# 	free_all_reg()
		# 	regn = free_reg()
		# 	while siz:
		# 		asmCode.append('lw '+regn+', '+str(off2)+'($fp)')
		# 		asmCode.append('sw '+regn+', '+str(off1)+'($fp)')
		# 		off1 += 4
		# 		off2 += 4
		# 		siz -= 4
		# 	regsState[regn] = 0

#####################################################################

		elif x=='=':
			if flag == 2:
				siz = info2.mysize
				off2 = info2.offset
				free_all_reg()
				regn = free_reg()
				reg1 = get_reg(arg1)

				off1 = 0
				while siz:
					asmCode.append('lw '+regn+', '+str(off2)+'($fp)')
					asmCode.append('sw '+regn+', '+str(off1)+'('+reg1+')')
					off1 += 4
					off2 += 4
					siz -= 4
				regsState[regn] = 0
				flag = 0

			elif flag == 3:
				siz = info1.mysize
				off1 = info1.offset
				free_all_reg()
				regn = free_reg()
				reg2 = get_reg(arg2)
				
				off2 = 0
				while siz:
					asmCode.append('lw '+regn+', '+str(off2)+'('+reg2+')')
					asmCode.append('sw '+regn+', '+str(off1)+'($fp)')
					off1 += 4
					off2 += 4
					siz -= 4
				regsState[regn] = 0
				flag = 0

			elif flag == 1:
				siz = 32
				off1 = 0
				off2 = 0
				free_all_reg()
				regn = free_reg()
				reg1 = get_reg(arg1)
				reg2 = get_reg(arg2)

				while siz:
					asmCode.append('lw '+regn+', '+str(off2)+'('+reg2+')')
					asmCode.append('sw '+regn+', '+str(off1)+'('+reg1+')')
					off1 += 4
					off2 += 4
					siz -= 4
				regsState[regn] = 0
				flag = 0

			else :
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
				regsState[regn] = 0		

###############################################################


				

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

		if flag == 1 or flag==2:
			asmCode.append('sw '+dest+', 0('+reg1+')')
			# only_empty(reg1)
			regsState[reg1] = 0
			return
		# if flag == 1 or flag == 2:
			# asmCode.append('sw '+dest+', 0('+reg1+')')
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
			cnt1 = 0
			while arg1.startswith('addr_'):
				arg1 = arg1[5:]
				cnt1+=1
			reg1 = get_reg(arg1)
			dest = free_reg()
			regsState[dest] = 1
			while cnt1>1:
				cnt1-=1
				asmCode.append('lw '+reg1+', 0('+reg1+')')
			asmCode.append('lw '+regs1+', 0('+reg1+')')

			asmCode.append('lw '+dest+', 0('+regs1+')')
			regsState[regs1] = 0
		else:
			dest = get_reg(arg0)

		if arg1.startswith('addr_'):
			src1 = free_reg()
			regsState[src1] = 1
			cnt2 = 0
			while arg1.startswith('addr_'):
				arg1 = arg1[5:]
				cnt2+=1
			reg2 = get_reg(arg1)
			while cnt2:
				cnt2-=1
				asmCode.append('lw '+reg2+', 0('+reg2+')')
			asmCode.append('move '+src1+', '+reg2)
			only_empty(reg2)
		else:
			src1 = get_reg(arg1)

		if arg2.startswith('addr_'):
			src2 = free_reg()
			regsState[src2] = 1
			cnt2 = 0
			while arg2.startswith('addr_'):
				arg2 = arg2[5:]
				cnt2+=1
			reg3 = get_reg(arg2)
			while cnt2:
				cnt2-=1
				asmCode.append('lw '+reg3+', 0('+reg3+')')
			asmCode.append('move '+src2+', '+reg3)
			only_empty(reg3)
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
		
		if x == '&':
			asmCode.append('and '+dest+', '+src1+', '+src2)
		
		if x == '|':
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
			only_empty(reg1)

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