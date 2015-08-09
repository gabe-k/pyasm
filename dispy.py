from dis import opname
import marshal
import sys
import types


def disassemble(s):
	i = 0
	#r = ''
	o = []
	while i < len(s):
		r = opname[ord(s[i])] + ' '
		if ord(s[i]) >= 90: # these are the ones with args
			r += str(ord(s[i+1]) | (ord(s[i+2]) << 8))
			i += 2
		i += 1
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
		write_list(f, o, indents, 'list')
	elif type(o) == types.NoneType:
		write_none(f, o, indents)
	elif type(o) == types.FloatType:
		write_float(f, o, indents)

def write_float(f, d, indents):
	f.write(('\t' * indents) + str(d) + '\n')

def write_none(f, s, indents):
	f.write(('\t' * indents) + 'none\n')

def write_string(f, s, indents):
	f.write(('\t' * indents) + 'string "' + s + '"\n')

def write_int(f, i, indents):
	f.write(('\t' * indents) + 'int ' + str(i) + '\n')

def write_list(f, l, indents, prefix):
	f.write(('\t' * indents) + prefix + ' ' + str(len(l)) + '\n')
	for i in l:
		write_object(f, i, indents + 1)
	f.write(('\t' * indents) + 'end\n')

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
	
	instructions = disassemble(c.co_code)
	f.write('\t' * (indents + 1))
	f.write('instructions\n')
	for i in instructions:
		f.write('\t' * (indents + 2))
		f.write(i)
		f.write('\n')

	f.write('\t' * (indents + 1))
	f.write('end\n')
	f.write('\t' * indents)
	f.write('end\n')

disassemble_file(sys.argv[1])
