#!/usr/local/bin/perl

use strict;
use Getopt::Long;
use Net::SNMP;

my $Version =			"1.2.1 20071018";
my $snmp_timeout = 		3;

my $cisco_stack_table =		"1.3.6.1.4.1.9.9.500.1.2.1.1.1";
my $cisco_stack_state =		"1.3.6.1.4.1.9.9.500.1.2.1.1.6";
my $cisco_stack_ring =		"1.3.6.1.4.1.9.9.500.1.1.3.0";

my $status =			"UNKNOWN";
my $session;
my $error;
my $result;
my $stackring_state;

my $o_debug =			0;
my $o_alarm =			0;
my $o_host;
my $o_community;
my $o_username;
my $o_authpass;
my $o_privpass;
my $o_authprot;
my $o_privprot;
my $o_snmpversion;
my $o_version;
my $o_help;

my %members;
my %ERRORS = (
	'OK'		=>	0,
	'WARNING'	=>	1,
	'CRITICAL'	=>	2,
	'UNKNOWN'	=>	3,
	'DEPENDENT'	=>	4,
);
my %STACK_STATES = (
         '1'		=>	'waiting',
         '2'		=>	'progressing',
         '3'		=>	'added',
         '4'		=>	'ready',
         '5'		=>	'sdmMismatch',
         '6'		=>	'verMismatch',
         '7'		=>	'featureMismatch',
         '8'		=>	'newMasterInit',
         '9'		=>	'provisioned',
         '10'		=>	'invalid',
);


##########################
#
#         MAIN
#
##########################

check_options();

if ( $o_snmpversion == 3 ) {
	($session, $error) = Net::SNMP->session(
		-hostname	=> $o_host,
		-version	=> $o_snmpversion,
		-username	=> $o_username,
		-authpassword	=> $o_authpass,
		-authprotocol	=> $o_authprot,
		-privpassword	=> $o_privpass,
		-privprotocol	=> $o_privprot,
		-port		=> 161,
		-timeout	=> $snmp_timeout
	);
}

else {
	($session, $error) = Net::SNMP->session(
		-hostname	=> $o_host,
		-community	=> $o_community,
		-port		=> 161,
		-timeout	=> $snmp_timeout
	);
}

if (!defined($session)) {
	printf("ERROR: %s.\n", $error);
	exit $ERRORS{"CRITICAL"};
}

#
# Get Cisco stack table
#
$result = $session->get_table(
		-baseoid => $cisco_stack_table
	);

if (!defined($result)) {
	printf("ERROR: %s.\n", $session->error);
	$session->close;
	exit $ERRORS{"CRITICAL"};
}

foreach my $key ( keys %{$result}) {
	my $id = ( $$result{$key} * 1000 ) + 1;
	my $oid = "$cisco_stack_state.$id";

	my $result2 = $session->get_request(
			-varbindlist	=> [$oid]
		);

	if (!defined($result2)) {
		printf("ERROR: %s.\n", $session->error);
		$session->close;
		exit $ERRORS{"CRITICAL"};
	}

	print "DEBUG: member = $$result{$key} -> oid = $oid -> state = " . $result2->{"$oid"} . "\n" if $o_debug;

	$members{$$result{$key}} = $result2->{"$oid"};
}

if ($o_alarm) {
	$members{"2"} = 6;
	print "-- SIMULATING ALARM -- ";
}

#
# Get Cisco stack ring speed if more than one stack member
#
if ( keys(%{$result}) > 1 ) {
	$result = $session->get_request(
			-varbindlist => [$cisco_stack_ring]
	);

	if (!defined($result)) {
		printf("ERROR: %s.\n", $session->error);
		$session->close;
		exit $ERRORS{"CRITICAL"};
	}

	#
	# Parse SNMP stack ring result
	#
	if ( $result->{$cisco_stack_ring} == 1 ) {
		$stackring_state = "Full";
	}
	else {
		$status = "WARNING";
		$stackring_state = "Half";
	}

	print "DEBUG: snmp_ring_state = " . $result->{$cisco_stack_ring} . " -> ring_state = $stackring_state\n" if $o_debug;
	print "Stack Ring: $stackring_state, ";
}

$session->close;

my $nitems = keys (%members);
my $n = 0;

foreach my $member (keys (%members)) {
	$n++;
	if ( $members{$member} == 4 or $members{$member} == 9 ) {
		if (( $status ne "CRITICAL" ) && ( $status ne "WARNING" )) {
			$status = "OK";
		}
	} else {
		$status = "CRITICAL";
	}
	print "Member $member: $STACK_STATES{$members{$member}}";
	if ($n < $nitems) {
		print ", ";
	} else {
		print "\n";
	}
}

print "DEBUG: $status: $ERRORS{$status}\n" if $o_debug;

exit $ERRORS{$status};

##########################
#
#         FUNCTIONS
#
##########################

sub version {
	print "$0 version: $Version\n";
}

sub usage {
	print <<DATA;

Usage: $0 [-V] [-h] [-D] [-T] -H <host> -C <community> [-a] [-A] [-x] [-X] [-u] -v <version>

-h, --help
   prints this help message
-V, --version
   prints version number
-D, --debug
   prints debug info. do not use in production.
-T, --test
   the plugin simulates an alarm without the need to break the stack!!!
-H, --hostname=HOST
   name or IP address of host to check
-C, --community=STRING NAME
   community name for the host's SNMP agent (implies v1/v2 protocol)
-a, --authprotocol=PROTOCOL
   authentication protocol, md5 or sha (if using v3 protocol)
-A, --authpassword=PASSWORD
   authentication password (if using v3 protocol)
-x, --privacyprotocol=PROTOCOL
   privacy protocol, des, 3des or aes (if using v3 protocol)
-X, --privacypassword=PASSWORD
   privacy password (if using v3 protocol)
-u, --username=USERNAME
   username (if using v3 protocol)
-v, --snmpversion=VERSION
   version, 1, 2 or 3

DATA
}

sub help {
	print <<DATA;

SNMP Cisco stack for Nagios version: $Version
Author: Andrea Gabellini - <andrea.gabellini\@telecomitalia.sm>
Check for stack's status of Cisco 3750

DATA

	usage();
}

sub check_options {
	Getopt::Long::Configure ("bundling");
	GetOptions(
		'h'     => \$o_help,    	'help'        	=> \$o_help,
		'V'	=> \$o_version,		'version'	=> \$o_version,
		'D'	=> \$o_debug,		'debug'		=> \$o_debug,
		'T'	=> \$o_alarm,		'TEST'		=> \$o_alarm,
		'H:s'   => \$o_host,		'hostname:s'	=> \$o_host,
		'C:s'	=> \$o_community,	'community:s'	=> \$o_community,
		'a:s'	=> \$o_authprot,	'authprotocol:s'	=> \$o_authprot,
		'A:s'	=> \$o_authpass,	'authpassword:s'	=> \$o_authpass,
		'x:s'	=> \$o_privprot,	'privprotocol:s'	=> \$o_privprot,
		'X:s'	=> \$o_privpass,	'privpassword:s'	=> \$o_privpass,
		'u:s'	=> \$o_username,	'username:s'		=> \$o_username,
		'v:i'	=> \$o_snmpversion,	'snmpversion:i'		=> \$o_snmpversion
	);
	if (defined ($o_help) ) {
		help();
		exit $ERRORS{"UNKNOWN"};
	}
	if (defined($o_version)) {
		version();
		exit $ERRORS{"UNKNOWN"};
	}
	if (!defined($o_host) ) {
		usage();
		exit $ERRORS{"UNKNOWN"};
	}
	if (!defined($o_snmpversion) ) {
		usage();
		exit $ERRORS{"UNKNOWN"};
	}
	if($o_snmpversion == 3) {
		if (!defined($o_authprot) ) {
			usage();
			exit $ERRORS{"UNKNWON"};
		}
		if (!defined($o_authpass) ) {
			usage();
			exit $ERRORS{"UNKNWON"};
		}
		if (!defined($o_privprot) ) {
			usage();
			exit $ERRORS{"UNKNWON"};
		}
		if (!defined($o_privpass) ) {
			usage();
			exit $ERRORS{"UNKNWON"};
		}
		if (!defined($o_username) ) {
			usage();
			exit $ERRORS{"UNKNWON"};
		}
	}
	else {
		if (!defined($o_community) ) {
			usage();
			exit $ERRORS{"UNKNOWN"};
		}
	}
	
}

