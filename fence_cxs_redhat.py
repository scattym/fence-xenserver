#!/usr/bin/python

# It's only just begun...
# Current status: completely unusable, try the fence_cxs.py script for the moment. This Red
# Hat compatible version is just in its' infancy.

# Copyright 2011 Matt Clark
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Please let me know if you are using this script so that I can work out
# whether I should continue support for it. mattjclark0407 at hotmail dot com


#import sys, re, pexpect
from fencing import *
import XenAPI


# Find the status of the port given in the -u flag of options.
def get_power_status(session, options):
	if( options["-u"] == "" ):
		return "bad"
	try:
		vm = session.xenapi.VM.get_by_uuid(options["-u"])
		record = session.xenapi.VM.get_record(vm);
		if not(record["is_a_template"]) and not(record["is_control_domain"]):
			status = record["power_state"]
			print "UUID:", record["uuid"], "NAME:", record["name_label"], "POWER STATUS:", record["power_state"]
			return (status=="Running" and "on" or "off")
	except Exception, exn:
		print str(exn);

# Set the state of the port given in the -n flag of options.
def set_power_status(session, options):
	if( uuid == "" ):
		return;
	
	try:
		vm = session.xenapi.VM.get_by_uuid(uuid)
		record = session.xenapi.VM.get_record(vm);
		if not(record["is_a_template"]) and not(record["is_control_domain"]):
			if( options["-o"] == "on" ):
				session.xenapi.VM.start(vm, False, True)
			elif( options["-o"] == "off" ):
				session.xenapi.VM.hard_shutdown(vm)
			elif( options["-o"] == "reboot" ):
				session.xenapi.VM.hard_reboot(vm)
	except Exception, exn:
		print str(exn);


def get_outlets_status(session, options):
	result = {}

	try:
		if( options["-u"] == "" ):
			vms = session.xenapi.VM.get_all()
		else:
			vms = [session.xenapi.VM.get_by_uuid(uuid)]
		for vm in vms:
			record = session.xenapi.VM.get_record(vm);
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				name = record["name_label"]
				uuid = record["uuid"]
				status = record["power_state"]
				result[uuid] = (name, status)
				print "UUID:", record["uuid"], "NAME:", name, "POWER STATUS:", record["power_state"]
	except Exception, exn:
		print str(exn);

	return result

def connectAndLogin(options):
	try:
		session = XenAPI.Session(options["-s"]);
	except Exception, exn:
		print str(exn);
		sys.exit(3);
	try:
		session.xenapi.login_with_password(options["-l"], options["-p"]);
	except Exception, exn:
		print str(exn);
		sys.exit(3);
	return session;

# Main agent method
def main():

	device_opt = [ "help", "version", "agent", "quiet", "verbose", "debug",
		       "action", "login", "passwd", "passwd_script",
		       "test", "separator", "no_login", "no_password",
		       "inet4_only","inet6_only",
		       "power_timeout", "shell_timeout", "login_timeout", "power_wait", "session_url", "uuid" ]

	atexit.register(atexit_handler)

	options=process_input(device_opt)

	options = check_input(device_opt, options)

	docs = { }
	docs["shortdesc"] = "Fence agent for Citrix XenServer"
	docs["longdesc"] = "fence_cxs_redhat" 
	show_docs(options, docs)

	xenSession = connectAndLogin(options)
	
	# Operate the fencing device
	result = fence_action(xenSession, options, set_power_status, get_power_status, get_outlets_status)

	sys.exit(result)

if __name__ == "__main__":
	main()
