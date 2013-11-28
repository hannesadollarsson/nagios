#!/usr/bin/python
import argparse
import sys
from ftplib import FTP

# define input arguments
parser = argparse.ArgumentParser(description='check_ftp_list usage')
parser.add_argument('-H', '--host',help='host address',required=True)
parser.add_argument('-u','--user',help='username',required=True)
parser.add_argument('-p','--password',help='password',required=True)
parser.add_argument('-d','--directory',help='working dir path',required=True)
parser.add_argument('-f','--file',help='watch file',required=True)

args = parser.parse_args()

# define variables
HOSTNAME = args.host
USER = args.user
PASSWORD = args.password
DIR = args.directory
FILE = args.file

# connect to host
ftp = FTP(HOSTNAME)
try:
    ftp.login(USER, PASSWORD)
except Exception:
    print "CRITICAL - Unable to connect to remote host"
    exit(2)

# change to working dir
try:
    ftp.cwd(DIR)
except Exception:
    print "WARNING - Unable to change remote directory" 
    exit(2)
    ftp.quit()

# get directory listing
DIR_LIST = ftp.nlst()

if FILE in DIR_LIST:
    print "OK - file exists"
    sys.exit(0)
else:
    print "WARNING - file does not exist"
    sys.exit(1)

# close connection
ftp.quit()
