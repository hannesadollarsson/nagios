#!/usr/bin/python
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-h1','--hop1',help='hop1address',required=True)

args = parser.parse_args()

IP = args.host
HOP1 = args.hop1
:q
def traceroute(IP):
	### Do traceroute
	cli_cmd = "/usr/bin/tracepaht " + IP
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

def check_hop1(IP, HOP1):
	### Check traceroute result for HOP1
	TRACE = traceroute(IP)

print check_hop1(IP, HOP1)
