#!/usr/bin/python

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
	f = open(filename.split('.')[0] + '.pyasm', 'w')
	write_object(f, c, 0, 1)
	f.close()

def write_object(f, o, indents, count):
	f.write('\t' * indents)
	if count > 1:
		f.write(int_to_str(count) + " * ")
	if type(o) == types.CodeType:
		f.write('code ')
		write_code(f, o, indents)
	elif type(o) == types.StringType:
		f.write('string ')
		write_string(f, o)
	elif type(o) == types.IntType:
		f.write('int ')
		write_int(f, o)
	elif type(o) == types.ListType:
		f.write('list ')
		write_list(f, o, indents)
	elif type(o) == types.TupleType:
		f.write('tuple ')
		write_list(f, o, indents)
	elif type(o) == types.NoneType:
		write_none(f, o)
	elif type(o) == types.FloatType:
		f.write('float ')
		write_float(f, o)

def write_float(f, d):
	f.write(str(d) + '\n')

def write_none(f, s):
	f.write('none\n')

def write_string(f, s):
	f.write('"' + s.encode("string-escape") + '"\n')

def int_to_str(i):
	if i != 0 and (i & 0xF == 0 or i & 0xF == 0xF):
		return hex(i)
	return str(i)

def write_int(f, i):
	f.write(int_to_str(i) + '\n')

def write_list(f, l, indents):
	f.write(str(len(l)) + '\n')
	dupe_count = 1
	i = 0
	while i < len(l):
		dupe_count = 1
		while i < len(l) - 1 and l[i] == l[i + 1]:
			dupe_count += 1
			i += 1

		write_object(f, l[i], indents + 1, dupe_count)
		i += 1

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
	f.write('\n')
	if c.co_argcount != 0:
		f.write('\t' * (indents + 1))
		f.write('arg_count ' + str(c.co_argcount) + '\n')
	if c.co_nlocals != 0:
		f.write('\t' * (indents + 1))
		f.write('n_locals ' + str(c.co_nlocals) + '\n')
	if c.co_stacksize != 0:
		f.write('\t' * (indents + 1))
		f.write('stack_size ' + str(c.co_stacksize) + '\n')
	if c.co_flags != 0:
		f.write('\t' * (indents + 1))
		f.write('flags ' + str(c.co_flags) + '\n')
	
	if len(c.co_consts) != 0:
		f.write('\t' * (indents + 1))
		f.write('consts ')
		write_list(f, c.co_consts, indents + 1)
	if len(c.co_names) != 0:
		f.write('\t' * (indents + 1))
		f.write('names ')
		write_list(f, c.co_names, indents + 1)
	if len(c.co_varnames) != 0:
		f.write('\t' * (indents + 1))
		f.write('varnames ')
		write_list(f, c.co_varnames, indents + 1)
	if len(c.co_freevars) != 0:
		f.write('\t' * (indents + 1))
		f.write('freevars ')
		write_list(f, c.co_freevars, indents + 1)
	if len(c.co_cellvars) != 0:
		f.write('\t' * (indents + 1))
		f.write('cellvars ')
		write_list(f, c.co_cellvars, indents + 1)

	instructions = disassemble(c)
	f.write('\t' * (indents + 1))
	f.write('instructions\n')
	for i in instructions:
		f.write('\t' * (indents + 2))
		f.write(i)
		f.write('\n')

	f.write('\t' * (indents + 1))
	f.write('end\n')
	f.write('\t' * (indents + 1))
	f.write('name ')
	write_string(f, c.co_name)
	f.write('\t' * (indents + 1))
	f.write('filename ')
	write_string(f, c.co_filename)
	f.write('\t' * (indents + 1))
	f.write('lnotab')
	write_string(f, c.co_lnotab)
	f.write('\t' * indents)
	f.write('end\n')

if __name__ == "__main__":
	disassemble_file(sys.argv[1])
