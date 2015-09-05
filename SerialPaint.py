#!/usr/bin/python2.7
import os,sys,serial,numpy,cv2
LEVEL = 1;
VERSION_NUMBER = 0x02;
FILE_HEADER_LENGTH = 32;
#Strange file if the header length is large than this number
PAINTER_CONFIG_STRING = "P0\n";
#Configure the mode of painter
ScanYFirst = False;
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
		GRAY_IMAGE = False;
		if painter_file_header[14:(14+4)] == 3:
			print("BGR Image");
		else:
			print("Byte per pixel:%u"%ords(painter_file_header[14:(14+4)],4));
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
	if ScanYFirst == True:
		while i < len(greyimg[0]):
			j = 0
			while j < len(greyimg):
				if greyimg[j][i] <= 127:#>127 is white,<= 127 is black
					dot_array.append([i,j,1]);#add a dot,i is X,j is Y,in level 1,1 means black
				j+=1;
			i+=1;
	else:#Scan X first
		while i < len(greyimg):
			j = 0
			while j < len(greyimg[0]):
				if greyimg[i][j] <= 127:#>127 is white,<= 127 is black
					dot_array.append([j,i,1]);#add a dot,j is X,i is Y,in level 1,1 means black
				j+=1;
			i+=1;
	return dot_array;
def send_dot_array(ser,dot_array):
	ser.write(PAINTER_CONFIG_STRING);
	i = 0;
	while i < len(dot_array):
		ser.write("%s\n"%dot_array[i]);
		i+=1;
def get_distance(x1,y1,x2,y2):
	return numpy.sqrt(pow(x1-x2,2)+pow(y1-y2,2));
def search_for_the_shortest_distance(way,unsearched_dot,dot_array_distance,zero_to_dot_distance):
	searchresults = [];
	i = 0;
	while i < len(unsearched_dot):
		new_unsearched_dot = unsearched_dot[:];
		new_way = way[:];
		new_way.append(new_unsearched_dot[i]);
		del(new_unsearched_dot[i]);
		if len(unsearched_dot) == 0:
			#It is empty
			break;
		#print(way,unsearched_dot);
		searchresult = search_for_the_shortest_distance(new_way,new_unsearched_dot,dot_array_distance,zero_to_dot_distance);
		searchresults.append(searchresult);
		i+=1;
	if len(unsearched_dot) > 0:
		#It is not empty
		minindex = 0;
		i = 1;
		while i < len(searchresults):
			if searchresults[i][1] < searchresults[minindex][1]:#Get the min length
				minindex = i;
			i+=1;
		length = searchresults[minindex][1];
		way = searchresults[minindex][0];
	else:
		length = zero_to_dot_distance[way[0]];#Get the distance of 0 to the first dot
		i = 0;
		while i < (len(way)-1):
			#print("Length",i,dot_array_distance[way[i]][way[i+1]]);
			length += dot_array_distance[way[i]][way[i+1]];
			i+=1;
		#print(length);
	return [way,length];
def get_shortest_distance(dot_array_distance,zero_to_dot_distance):
	way = [];
	searchresult = search_for_the_shortest_distance(way,range(len(dot_array_distance)),dot_array_distance,zero_to_dot_distance);
	#print(searchresult);
	return searchresult[0];#searchresult[0] is the way searchresult[1] is the length
def get_the_shortest_dot_array(dot_array):
	dot_array_distance = [];
	new_dot_array = [];
	i = 0;
	while i < len(dot_array):
		dot_array_distance.append([]);
		j = 0;
		while j < len(dot_array):
			if i != j:
				dot_array_distance[i].append(get_distance(dot_array[i][1],dot_array[i][0],dot_array[j][1],dot_array[j][0]));
				#Get every two dots' distance,0 means X,1 means Y
			else:
				dot_array_distance[i].append(0);#The distance to itself
			j += 1;
		i += 1;
	zero_to_dot_distance = [];
	i = 0;
	while i < len(dot_array):
		zero_to_dot_distance.append(get_distance(0,0,dot_array[i][1],dot_array[i][0]));#Set the distance from 0 to every dot
		i += 1;
	print(dot_array_distance);
	print(zero_to_dot_distance);
	searchresult = get_shortest_distance(dot_array_distance,zero_to_dot_distance);
	i = 0;
	while i < len(searchresult):
		new_dot_array.append(dot_array[searchresult[i]]);
		i += 1;
	return new_dot_array;
if __name__ == '__main__':
	if len(sys.argv) == 2:
		if LEVEL == 1:
			ser = serial.serial_for_url("hwgrep://2341:8036",do_not_open = False,baudrate=115200,timeout=1);#VID:PID
			print("Painter Port:%s\n"%ser.port);
			grayimg = decode(sys.argv[1]);
			#print(grayimg);
			dot_array = get_dot_array(grayimg);
			#print(dot_array);
			dot_array = get_the_shortest_dot_array(dot_array);
			print(dot_array);
			#If you want,you can comment it,it will be a little slow if you use it.
			#For Debug
			#send_dot_array(sys.stderr,dot_array);
			send_dot_array(ser,dot_array);
			ser.close();
		else:
			sys.stderr.write("Only support LEVEL 1\n");
			sys.exit(2);
	else:
		sys.stderr.write("%s [painter file]\nPaint painer file(.paf).\n"%(sys.argv[0]));
		os.system("pause");#For Windows
		sys.exit(1);
