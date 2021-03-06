#!/usr/bin/python
import argparse
import sys
import subprocess

parser = argparse.ArgumentParser(description='test')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-v','--version',help='snmp v1, 2 or 3',required=True)
parser.add_argument('-C','--community',help='community or v3 params,usn:authproto:authpass:privproto:privpass:level',required=True)

args = parser.parse_args()

HOST = args.host
VERSION = args.version
COMMUNITY = args.community

STACK_TABLE_OID = "1.3.6.1.4.1.9.9.500.1.2.1.1.1"
STACK_STATE_OID = "1.3.6.1.4.1.9.9.500.1.2.1.1.6"
STACK_RING_OID  = "1.3.6.1.4.1.9.9.500.1.1.3.0"

def get_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, OID):
    cli_cmd = "/usr/bin/snmpwalk -v 3" + " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + HOST + " " + OID
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, OID):
    cli_cmd = "/usr/bin/snmpwalk -v 3" + " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + HOST + " " + OID
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_snmp(HOST, VERSION, COMMUNITY, OID):
    cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + HOST + " " + OID
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_snmp(HOST, VERSION, COMMUNITY, OID):
    cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + HOST + " " + OID
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

if VERSION == "3":
    COMMUNITY = COMMUNITY.split(':')
    USN = COMMUNITY[0]
    AUTHPROT = COMMUNITY[1]
    AUTHPASS = COMMUNITY[2]
    PRIVPROT = COMMUNITY[3]
    PRIVPASS = COMMUNITY[4]
    AUTHLEV = COMMUNITY[5]

    STACK_TABLE = get_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, STACK_TABLE_OID)
    STACK_STATE = get_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, STACK_STATE_OID)
    STACK_RING = get_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV, STACK_RING_OID)
    
elif VERSION == "2" or VERSION == "1":
    STACK_TABLE = get_snmp(HOST, VERSION, COMMUNITY, STACK_TABLE_OID)
    STACK_STATE = get_snmp(HOST, VERSION, COMMUNITY, STACK_STATE_OID)
    STACK_RING = get_snmp(HOST, VERSION, COMMUNITY, STACK_RING_OID)
else:
	 sys.exit("Invalid version, use 1, 2 or 3")

print STACK_TABLE[0]
print STACK_STATE[0]
print STACK_RING[0]
