#!/usr/bin/python
import argparse
import sys
import subprocess
# define input arguments
parser = argparse.ArgumentParser(description='test')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-v','--version',help='snmp version (1,2,3)',required=True)
parser.add_argument('-C','--community',help='community or authentication params if version 3, usn:authproto:authpass:privproto:privpass:level',required=True)
parser.add_argument('-p','--peer',help='vpn peer address',required=True)


args = parser.parse_args()

IP = args.host
VERSION = args.version
COMMUNITY = args.community
PEER = args.peer
STATE = "CRITICAL"

def get_state_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV):
	cli_cmd = "/usr/bin/snmpwalk -v 3" +  " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + IP + " 1.3.6.1.4.1.9.9.171.1.2.3.1.7"
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

def get_state_snmp(IP, VERSION, COMMUNITY, PEER):
	cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + IP + " 1.3.6.1.4.19.9.171.1.2.3.1.7"
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output
	
if VERSION == "3":
	# split community into snmpv3 parameters
	COMMUNITY = COMMUNITY.split(':')
	USN = COMMUNITY[0]
	AUTHPROT = COMMUNITY[1]
	AUTHPASS = COMMUNITY[2]
	PRIVPROT = COMMUNITY[3]
	PRIVPASS = COMMUNITY[4]
	AUTHLEV = COMMUNITY[5]
		
	UPTUNNELS = get_state_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV)
		
elif VERSION == "2" or VERSION == "1":
	UPTUNNELS = get_state_snmp(IP, VERSION, COMMUNITY)
else:
	sys.exit("Invalid version, use 1, 2 or 3")

if PEER in UPTUNNELS[0]:
	STATE = "OK"
	print "OK - VPN tunnel " + PEER + " is up"
	# Return result "OK" to Nagios
	sys.exit(0)
#else:
	print "CRITICAL - VPN tunnel " + PEER + " is down"
	# Return result "Critical" to Nagios
	sys.exit(2)
