#!/usr/bin/python
import argparse
import sys
import subprocess

parser = argparse.ArgumentParser(description='test')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-v','--version',help='snmp v1, 2 or 3',required=True)
parser.add_argument('-C','--community',help='community or v3 params,usn:authproto:authpass:privproto:privpass:level',required=True)
parser.add_argument('-s','--state',help='active or standby',required=True)

args = parser.parse_args()

HOST = args.host
VERSION = args.version
COMMUNITY = args.community
STATE = args.state

# OIDs
HSRP_OP = "1.3.6.1.4.1.9.9.106.1.2.1.1.15"

# HSRP states
HSRP_ACTIVE = "6"
HSRP_STANDBY = "5"

def get_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV):
    cli_cmd = "/usr/bin/snmpwalk -v 3" + " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + HOST + " " + HSRP_OP
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_state_snmp(HOST, VERSION, COMMUNITY):
    cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + HOST + " " + HSRP_OP
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

    HSRP_STATE = get_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV)

elif VERSION == "2" or VERSION == "1":
    HSRP_STATE = get_state_snmp(HOST, VERSION, COMMUNITY)
else:
    sys.exit("Invalid version, use 1, 2 or 3")

# We only need the integer status    
HSRP_STATE = str(HSRP_STATE[0])    
HSRP_STATE = HSRP_STATE.split()
HSRP_STATE = HSRP_STATE[3]

# specifics checks
if STATE == "active":
    if HSRP_STATE is HSRP_ACTIVE:
        print "OK - Primary node is active"
        sys.exit(0)
    elif HSRP_STATE is HSRP_STANDBY:
        print "WARNING - Primary node is standby"
        sys.exit(1)
    else:
        print "CRITICAL - Primary node not in an operational state"
        sys.exit(2)

elif STATE == "standby":
    if HSRP_STATE is HSRP_STANDBY:
        print "OK - Secondary node is standby"
        sys.exit(0)
    elif HSRP_STATE is HSRP_ACTIVE:
        print "WARNING - Secondary node is active"
        sys.exit(1)
    else:
        print "CRITICAL - Secondary node not in an operational state"
        sys.exit(2)

else:
    print "Unknown state specified, please use active or standby"
    sys.exit(2)
