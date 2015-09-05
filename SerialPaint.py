#!/usr/bin/python2.7
import os,sys,serial,numpy,cv2
LEVEL = 1
VERSION_NUMBER = 0x02;
FILE_HEADER_LENGTH = 32;
#Strange file if the header length is large than this number
PAINTER_CONFIG_STRING = "P0\n";
#Configure the mode of painter
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
	img = numpy.zeros([ords(painter_file_header[6:(6+4)],4),ords(painter_file_header[10:(10+4)],4),ords(painter_file_header[14:(14+4)],4)], numpy.uint8);
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
			k = 0;
			while k < ords(painter_file_header[14:(14+4)],4):
				img[i,j,k] = ord(painter_file.read(1));
				#It may get BGR or Grey Value
				k+=1;
			j+=1;
		i+=1;
	painter_file.close();
	if GRAY_IMAGE == False:
		grayimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY);
	else:
		grayimg = img;
	return grayimg
def get_dot_array(greyimg):
	i = 0;
	dot_array = [];
	while i < len(greyimg):
		j = 0
		while j < len(greyimg[0]):
			if greyimg[i][j] <= 127:#>127 is white,<= 127 is black
				dot_array.append([i,j,1]);#add a dot,in level 1,1 means black
			j+=1;
		i+=1;
	return dot_array;
def send_dot_array(ser,dot_array):
	ser.write(PAINTER_CONFIG_STRING);
	i = 0;
	while i < len(dot_array):
		ser.write("%s\n"%dot_array[i]);
		i+=1;
if __name__ == '__main__':
	if len(sys.argv) == 2:
		ser = serial.serial_for_url("hwgrep://2341:8036",do_not_open = False,baudrate=115200,timeout=1);#VID:PID
		print("Painter Port:%s\n"%ser.port);
		if LEVEL == 1:
			grayimg = decode(sys.argv[1]);
			print(grayimg);
			dot_array = get_dot_array(grayimg);
			print(dot_array);
			#For Debug
			#send_dot_array(sys.stderr,dot_array);
			send_dot_array(ser,dot_array);
			ser.close();
		else:
			sys.stderr.write("Only support LEVEL 1\n");
			ser.close();
			sys.exit(2);
	else:
		sys.stderr.write("%s [painter file]\nPaint painer file(.paf).\n"%(sys.argv[0]));
		os.system("pause");#For Windows
		sys.exit(1);
