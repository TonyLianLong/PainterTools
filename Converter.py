#!/usr/bin/python2.7
import os,sys,cv2
#Need NumPy,OpenCV
default_painter_file_path = "Output.paf";
#default output file
VERSION_NUMBER = 0x01;
FILE_HEADER_LENGTH = 32;
#It will fill the unused bytes of header with NULL
def chrs(number,char_number):
	#Turn large numbers into many ASCII characters
	str = "";
	while char_number>0:
		char_number -= 1;
		str+=chr((number>>(char_number*8))&0xFF);
	return str
def write_painter_file_header(painter_file,img):
	file_header_str = "PAF" + chr(0x7F) + chr(VERSION_NUMBER) + chr(FILE_HEADER_LENGTH) + chrs(len(img),4) + chrs(len(img[0]),4) + chrs(len(img[0][0]),4);
	if(len(file_header_str)<=FILE_HEADER_LENGTH):
		i = len(file_header_str);
		while i<32:
			file_header_str += chr(0x00);#Fill unused first 32 bytes with NULL
			i+=1;
	else:
		sys.stderr.write("Warning:File header string is too long");
	painter_file.write(file_header_str);
def convert(image_file_path,painter_file_path):
	img = cv2.imread(image_file_path);
	painter_file = open(painter_file_path,"wb");
	write_painter_file_header(painter_file,img);
	i = 0
	while i < len(img):
		j = 0
		while j < len(img[0]):
			k = 0
			while k < len(img[0][0]):
				painter_file.write(img[i,j,k]);
				k+=1
			j+=1
		i+=1
	painter_file.close();
if __name__ == '__main__':
	if len(sys.argv) == 2:
		convert(sys.argv[1],default_painter_file_path);
	elif len(sys.argv) == 3:
		convert(sys.argv[1],sys.argv[2]);
	else:
		sys.stderr.write("%s [image file] [output file]\nConvert image file to painter file(.paf).\n"%(sys.argv[0]));
		os.system("pause");#For Windows
		sys.exit(1)
