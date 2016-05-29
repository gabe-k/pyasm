from dis import opname, opmap
import marshal
import sys
import types

def disassemble(s):
	i = 0
	#r = ''
	o = []
	dupe_count = 1
	while i < len(s.co_code):
		op = ord(s.co_code[i])
		r = opname[op] + ' '
		if op >= 90: # these are the ones with args
			oparg = ord(s.co_code[i+1]) | (ord(s.co_code[i+2]) << 8)
			r += int_to_str(oparg)
			i += 2
		i += 1
		comment = generate_autocomment(s, op, oparg)
		if comment:
			r += " # " + comment
		if len(o) > 0 and (r == o[-1] or r == o[-1].split(' ', 2)[-1]):
			dupe_count += 1
			o[-1] = int_to_str(dupe_count) + " * " + r
			continue
		else:
			dupe_count = 1
		o.append(r)
	return o

def disassemble_file(filename):
	o = open(filename, 'rb')
	o.read(8)
	c = marshal.load(o)
	o.close()
	#print disassemble(c.co_code)
	f = open(filename.split('.')[0] + '.pyasm', 'w')
	write_object(f, c, 0)
	f.close()

def write_object(f, o, indents):
	if type(o) == types.CodeType:
		write_code(f, o, indents)
	elif type(o) == types.StringType:
		write_string(f, o, indents)
	elif type(o) == types.IntType:
		write_int(f, o, indents)
	elif type(o) == types.ListType:
		write_list(f, o, indents, 'list')
	elif type(o) == types.TupleType:
		write_list(f, o, indents, 'tuple')
	elif type(o) == types.NoneType:
		write_none(f, o, indents)
	elif type(o) == types.FloatType:
		write_float(f, o, indents)

def write_float(f, d, indents):
	f.write(('\t' * indents) + str(d) + '\n')

def write_none(f, s, indents):
	f.write(('\t' * indents) + 'none\n')

def write_string(f, s, indents, prefix='string'):
	f.write(('\t' * indents) + prefix + ' "' + s.encode("string-escape") + '"\n')

def int_to_str(i):
	if i & 0xF == 0 or i & 0xF == 0xF:
		return hex(i)
	return str(i)

def write_int(f, i, indents):
	f.write(('\t' * indents) + 'int ' + int_to_str(i) + '\n')

def write_list(f, l, indents, prefix):
	f.write(('\t' * indents) + prefix + ' ' + str(len(l)) + '\n')
	for i in l:
		write_object(f, i, indents + 1)
	f.write(('\t' * indents) + 'end\n')

def generate_autocomment(c, instruction, oparg):
	if instruction == opmap['LOAD_CONST'] and oparg < len(c.co_consts):
		return str(c.co_consts[oparg])
	elif instruction == opmap['LOAD_FAST'] or instruction == opmap['STORE_FAST'] and oparg < len(c.co_varnames):
		return str(c.co_varnames[oparg])
	elif instruction == opmap['LOAD_NAME'] or instruction == opmap['STORE_NAME'] and oparg < len(c.co_names):
		return str(c.co_names[oparg])
	return None

def write_code(f, c, indents):
	f.write('\t' * indents)
	f.write('code\n')
	f.write('\t' * (indents + 1))
	f.write('arg_count ' + str(c.co_argcount) + '\n')
	f.write('\t' * (indents + 1))
	f.write('n_locals ' + str(c.co_nlocals) + '\n')
	f.write('\t' * (indents + 1))
	f.write('stack_size ' + str(c.co_stacksize) + '\n')
	f.write('\t' * (indents + 1))
	f.write('flags ' + str(c.co_flags) + '\n')
	
	write_list(f, c.co_consts, indents + 1, 'consts')
	write_list(f, c.co_names, indents + 1, 'names')
	write_list(f, c.co_varnames, indents + 1, 'varnames')
	write_list(f, c.co_freevars, indents + 1, 'freevars')
	write_list(f, c.co_cellvars, indents + 1, 'cellvars')

	instructions = disassemble(c)
	f.write('\t' * (indents + 1))
	f.write('instructions\n')
	for i in instructions:
		f.write('\t' * (indents + 2))
		f.write(i)
		f.write('\n')

	f.write('\t' * (indents + 1))
	f.write('end\n')
	write_string(f, c.co_name, indents + 1, 'name')
	write_string(f, c.co_filename, indents + 1, 'filename')
	write_string(f, c.co_lnotab, indents + 1, 'lnotab')
	f.write('\t' * indents)
	f.write('end\n')

if __name__ == "__main__":
	disassemble_file(sys.argv[1])
