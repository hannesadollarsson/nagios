#!/usr/bin/python
import paramiko
import sys
import argparse

parser = argparse.ArgumentParser(description='Usage')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-u','--username',help='username',required=True)
parser.add_argument('-p','--password',help='password',required=True)
parser.add_argument('-w','--warning',help='warning %',required=True)
parser.add_argument('-c','--critical',help='critical %',required=True)

args = parser.parse_args()

HOST = args.host
USERNAME = args.username
PASSWORD = args.password
WARNING = args.warning
CRITICAL = args.critical

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(HOST, username=USERNAME, password=PASSWORD)
stdin, stdout, stderr = ssh.exec_command("show platform tcam utilization")
data = stdout.readlines()
ssh.close()

data_row = data[5]
data_row = data_row.split()

max_data = data_row[3].split('/')
used_data = data_row[4].split('/')

max_mask = max_data[0]
max_value = max_data[1]
used_mask = used_data[0]
used_value = used_data[1]
warning_threshold = float(WARNING) / 100
critical_threshold = float(CRITICAL) / 100

used_percent_mask = float(used_mask) / float(max_mask)
used_percent_mask = round(used_percent_mask, 2)
used_percent_value = float(used_value) / float(max_value)
used_percent_value = round(used_percent_value, 2)

if used_percent_mask >= critical_threshold:
	print "CRITICAL - Unicast mac address mask tcam utilization is above " + CRITICAL + " percent!"
	sys.exit(2)
elif used_percent_value >= critical_threshold:
	print "CRITICAL - Unicast mac address value tcam utilization is above " + CRITICAL + " percent!"
	sys.exit(2)
elif used_percent_mask >= warning_threshold:
	print "WARNING - Unicast mac address mask tcam utilization is above " + WARNING + " percent!"
	sys.exit(1)
elif used_percent_value >= warning_threshold:
	print "WARNING - Unicast mac address value tcam utilization is above " + WARNING + " percent!"
	sys.exit(1)
else:
	print "OK - Unicast mac address tcam utilization is below defined thresholds"
	sys.exit(0)
