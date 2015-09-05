#!/usr/bin/python2.7
import os,sys,serial
if __name__ == '__main__':
	ser = serial.serial_for_url("hwgrep://2341:8036",do_not_open = True,timeout=1)#VID:PID
	print("Painter Port:%s\n"%ser.port);
	sys.exit(0);
