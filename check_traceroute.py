#!/usr/bin/python
import argparse
import subprocess
import sys

parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('-t','--target',help='target address',required=True)
parser.add_argument('-h2','--hop2',help='hop2 address',required=True)

args = parser.parse_args()

IP = args.target
HOP2 = args.hop2

def traceroute(IP):
	### Do traceroute
	cli_cmd = "/usr/bin/tracepath " + IP
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

def check_hop(IP, HOP2):
	### Check traceroute result for HOP1
	TRACE = traceroute(IP)
	TRACE = TRACE[0]
	TRACE = TRACE.split()
	COUNT = 0
	
	for i in TRACE:
		if i == "2:":
			H2POS = COUNT+1
			if TRACE[H2POS] == HOP2:
				print "OK - Using primary path"
				sys.exit(0)
		COUNT += 1
	print "CRITICAL - Using secondary path"
	sys.exit(2)

check_hop(IP, HOP2)
