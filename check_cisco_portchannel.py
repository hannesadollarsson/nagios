#!/usr/bin/python
import argparse
import sys
import subprocess
# define input arguments
parser = argparse.ArgumentParser(description='test')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-v','--version',help='snmp version (1,2,3)',required=True)
parser.add_argument('-C','--community',help='community or authentication params if version 3, usn:authproto:authpass:privproto:privpass:level',required=True)
parser.add_argument('-p','--portchannel',help='specify portchannel number',required=True)

args = parser.parse_args()

IP = args.host
VERSION = args.version
COMMUNITY = args.community
PO = args.portchannel
PO_STATUS = "2"
PO_SPEED = "Gauge32: 1000"
UP_STATE = "INTEGER: 1"
FULL_BW = "Gauge32: 2000"
HALF_BW = "Gauge32: 1000"
OK = 0
WARNING = 1
UNKNOWN = 3

def convert_portchannel_number(PO):
	### Get SNMP portchannel number ###
	if int(PO) < 10:
		PO = "500" + PO
	else:
		PO = "50" + PO
	return PO

def get_status_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, PO):
	cli_cmd = "/usr/bin/snmpwalk -v 3" +  " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + IP + " 1.3.6.1.2.1.2.2.1.8." + PO
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

def get_speed_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, PO):
	cli_cmd = "/usr/bin/snmpwalk -v 3" +  " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + IP + " 1.3.6.1.2.1.31.1.1.1.15." + PO
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output
	
def get_status_snmp(IP, VERSION, COMMUNITY, PO):
	cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + IP + " 1.3.6.1.2.1.2.2.1.8." + PO
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

def get_speed_snmp(IP, VERSION, COMMUNITY, PO):
	cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + IP + " 1.3.6.1.2.1.31.1.1.1.15." + PO
	process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = process.communicate()
	return output

PO_SNMP = convert_portchannel_number(PO)
	
if VERSION == "3":
	# split community into snmpv3 parameters
	COMMUNITY = COMMUNITY.split(':')
	USN = COMMUNITY[0]
	AUTHPROT = COMMUNITY[1]
	AUTHPASS = COMMUNITY[2]
	PRIVPROT = COMMUNITY[3]
	PRIVPASS = COMMUNITY[4]
	AUTHLEV = COMMUNITY[5]
		
	PO_STATUS = get_status_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, PO_SNMP)
	PO_SPEED = get_speed_snmpv3(IP, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, PO_SNMP)
		
elif VERSION == "2" or VERSION == "1":
	PO_STATUS = get_status_snmp(IP, VERSION, COMMUNITY, PO_SNMP)
	PO_SPEED = get_speed_snmp(IP, VERSION, COMMUNITY, PO_SNMP)
else:
	sys.exit("Invalid version, use 1, 2 or 3")

if UP_STATE in PO_STATUS[0] and FULL_BW in PO_SPEED[0]:
	print "OK - Port-channel " + PO + " is up with with full bandwidth"
	# Return result "OK" to Nagios
	sys.exit(0)
elif UP_STATE in PO_STATUS[0] and HALF_BW in PO_SPEED[0]:
	print "WARNING - Port-channel " + PO + " is up with reduced bandwidth"
	sys.exit(1)
else:
	print "CRITICAL - Port-channel " + PO + " is down"
	# Return result "Critical" to Nagios
	sys.exit(2)
