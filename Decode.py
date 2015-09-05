#!/usr/bin/python2.7
import os,sys
VERSION_NUMBER = 0x02;
FILE_HEADER_LENGTH = 32;
#Strange file if the header length is large than this number
def chrs(number,char_number):
	#Turn a large number into many ASCII characters
	str = "";
	while char_number>0:
		char_number -= 1;
		str+=chr((number>>(char_number*8))&0xFF);
	return str
def ords(str,char_number):
	#Turn a large number storaged as ASCII characters into a simple number
	i = 0;
	num = 0;
	while i<char_number:
		num|=(ord(str[i])<<((char_number-1-i)*8));
		i += 1;
	return num
def verify_painter_file_header(painter_file_header):
	correct_file_header_str = "PAF" + chr(0x7F) + chr(VERSION_NUMBER) + chr(FILE_HEADER_LENGTH);
	if painter_file_header[0:6] != correct_file_header_str:
		sys.stderr.write("Painter file header is not correct.\n");
		sys.exit(2)
def decode(painter_file_path):
	painter_file = open(painter_file_path,"rb");
	painter_file_header = painter_file.read(FILE_HEADER_LENGTH);
	verify_painter_file_header(painter_file_header);
	if ords(painter_file_header[14:(14+4)],4) == 1:
		GRAY_IMAGE = True;
		print("Gray Image");
	else:
		print("Byte per pixel:%u"%ords(painter_file_header[14:(14+4)],4));
		GRAY_IMAGE = False;
	if painter_file_header[14:(14+4)] == 3:
		print("BGR Image");
	i = 0
	while i < ords(painter_file_header[6:(6+4)],4):
		j = 0
		while j < ords(painter_file_header[10:(10+4)],4):
			k = 0
			while k < ords(painter_file_header[14:(14+4)],4):
				sys.stdout.write("%u "%ord(painter_file.read(1)));
				#It may print as BGR or Grey Value
				k+=1
			sys.stdout.write("\n");
			j+=1
		i+=1
	painter_file.close();
if __name__ == '__main__':
	if len(sys.argv) == 2:
		decode(sys.argv[1]);
	else:
		sys.stderr.write("%s [painter file]\nDecode painter file(.paf) and print the data on to the console.\n"%(sys.argv[0]));
		os.system("pause");#For Windows
		sys.exit(1)
