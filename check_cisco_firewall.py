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

def get_primary_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV):
    primary_status = " 1.3.6.1.4.1.9.9.147.1.2.1.1.1.3.6"
    cli_cmd = "/usr/bin/snmpwalk -v 3" + " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + HOST + primary_status
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_secondary_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV):
    secondary_status = " 1.3.6.1.4.1.9.9.147.1.2.1.1.1.3.7"
    cli_cmd = "/usr/bin/snmpwalk -v 3" + " -a " + AUTHPROT + " -A " + AUTHPASS + " -x " + PRIVPROT + " -X " + PRIVPASS + " -u " + USN + " -l " + AUTHLEV + " " + HOST + secondary_status
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_primary_state_snmp(HOST, VERSION, COMMUNITY):
    primary_status = " 1.3.6.1.4.1.9.9.147.1.2.1.1.1.3.6"
    cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + HOST + primary_status
    process = subprocess.Popen(cli_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
    output = process.communicate()
    return output

def get_secondary_state_snmp(HOST, VERSION, COMMUNITY):
    secondary_status = " 1.3.6.1.4.1.9.9.147.1.2.1.1.1.3.7"
    cli_cmd = "/usr/bin/snmpwalk -v " + VERSION + " -c " + COMMUNITY + " " + HOST + secondary_status
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

    PRIMARY_STATE = get_primary_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV)
    SECONDARY_STATE = get_secondary_state_snmpv3(HOST, USN, AUTHPROT, AUTHPASS, PRIVPROT, PRIVPASS, AUTHLEV)

elif VERSION == "2" or VERSION == "1":
    PRIMARY_STATE = get_primary_state_snmp(HOST, VERSION, COMMUNITY)
    SECONDARY_STATE = get_secondary_state_snmp(HOST, VERSION, COMMUNITY)
else:
    sys.exit("Invalid version, use 1, 2 or 3")

# We only want the real return value
PRIMARY_STATE = str(PRIMARY_STATE)
SECONDARY_STATE = str(PRIMARY_STATE)
PRIMARY_STATE = PRIMARY_STATE[0].split(':')
SECONDARY_STATE = PRIMARY_STATE[0].split(':')

if PRIMARY_STATE[1] == "9" and SECONDARY_STATE[1] == "10":
    active_nodes = "2"
    print "OK - Primary is ACTIVE and secondary is STANDBY. " + active_nodes + " active nodes"
    sys.exit(0)
elif PRIMARY_STATE[1] == "10" and SECONDARY_STATE[1] == "9":
    active_nodes = "2"
    print "WARNING - Primary is STANDBY and secondary is ACTIVE. " + active_nodes + " active nodes"
    sys.exit(1)
elif PRIMARY_STATE[1] == "9" and SECONDARY_STATE[1] == "4":
    active_nodes = "1"
    print "WARNING - Primary is up and secondary is ERROR. " + active_nodes + " active node"
    sys.exit(1)
elif PRIMARY_STATE[1] == "4" and SECONDARY_STATE[1] == "9":
    active_nodes = "1"
    print "CIRITICAL - Primary is ERROR and secondary is ACTIVE. " + active_nodes + " active node"
    sys.exit(2)
elif PRIMARY_STATE[1] == "3" or SECONDARY_STATE[1] == "3":
    active_nodes = "1"
    print "CRITICAL - Primary or secondary is DOWN. " + active_nodes + " active node"
    sys.exit(2)
else:
    print "UNKNOWN STATUS"
    sys.exit(2)