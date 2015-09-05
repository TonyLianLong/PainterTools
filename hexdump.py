#!/usr/bin/python2.7
import sys
NUMBER_PER_LINE = 16
CAPITAL = True
if len(sys.argv) == 2:
	hex_file = open(sys.argv[1],"rb");
	file_offset = 0;
	file_finished = False;
	while file_finished == False:
		sys.stdout.write("0x%x\t"%file_offset);
		i = 0;
		while i < NUMBER_PER_LINE:
			char_read = hex_file.read(1);
			if len(char_read) == 0:
				file_finished = True;
				break;
			if CAPITAL == True:
				sys.stdout.write("%02X"%ord(char_read));
			else:
				sys.stdout.write("%02x"%ord(char_read));
			i +=1;
			if i != NUMBER_PER_LINE:
				sys.stdout.write(" ");
			else:
				sys.stdout.write("\n");
		file_offset += NUMBER_PER_LINE;
else:
	sys.stderr.write("%s [Hex File]\nDump hex file.\n"%sys.argv[0]);