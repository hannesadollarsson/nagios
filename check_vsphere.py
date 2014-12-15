#!/usr/bin/python
from pysphere import VIServer, VIProperty
import argparse
import sys

# required arguments
parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('-H', '--host', help='host address', required=True)
parser.add_argument('-u', '--username', help='username', required=True)
parser.add_argument('-p', '--password', help='password', required=True)
parser.add_argument('-c', '--count', help='host count', required=True)

# parse arguments
args = parser.parse_args()
host = args.host
username = args.username
password = args.password
count = args.count

# convert count to int
count = int(count)

# create server object
server = VIServer()

try:
    # connected to server
    server.connect(host, username, password)

except Exception:
    print "CRITICAL - Unable to connect to vSphere"
    sys.exit(2)

# collect dict of hosts
hosts = server.get_hosts()

# create an integer to track number of operational and down hosts
hosts_operational = 0
hosts_down = 0

# verify that we got information
if hosts:

    # get properties
    props = server._retrieve_properties_traversal(property_names=['name', 'runtime.connectionState'], obj_type="HostSystem")
        
    # get powerState for each host
    for prop_set in props:
        for prop in prop_set.PropSet:
            # add host to correct count based on runtime powered state
            if prop.Val == "connected":
                hosts_operational = hosts_operational + 1
            else:
                hosts_down = hosts_down + 1

else:
    print "CRITICAL - Unable to retrieve hosts"
    sys.exit(2)

# disconnect from vcenter
server.disconnect()

# verify we got the right host count
if len(hosts) == count and hosts_operational == count:
    print "OK - vSphere running, all hosts online"
    sys.exit(0)
elif len(hosts) == count and hosts_operational != count:
    print "WARNING - vSphere running, but only operational on " + str(hosts_operational) + " hosts out of " + str(len(hosts))
    sys.exit(1)
elif len(hosts) < count:
    print "WARNING - vSphere returned only " + str(len(hosts)) + " hosts, specified number of hosts is: " + str(count)
    sys.exit(1)
elif len(hosts) > count:
    print "WARNING - vSphere returned " + str(len(hosts)) + " hosts, more than specified"
    sys.exit(1)
else:
    print "CRITICAL - vSphere running, no active hosts"
    sys.exit(2)
