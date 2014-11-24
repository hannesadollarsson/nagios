#!/usr/bin/python
import paramiko
import sys
import argparse

parser = argparse.ArgumentParser(description='Usage')
parser.add_argument('-H','--host',help='hostaddress',required=True)
parser.add_argument('-u','--username',help='username',required=True)
parser.add_argument('-p','--password',help='password',required=True)

args = parser.parse_args()

HOST = args.host
USERNAME = args.username
PASSWORD = args.password

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(HOST, username=USERNAME, password=PASSWORD)
stdin, stdout, stderr = ssh.exec_command("show access-list")
data = stdout.readlines()

print type(data)

ssh.close()
