#!/usr/bin/env python
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

import sys, string, getopt
import XenAPI

def usage():
	print "Usage: fence_cxs [-hv] [-a <action>] -l <login username> -p <login password> -s <session url> [-u <UUID>]"
	print "Where:-"
	print "    -a : Specifies the action to perfom. Can be any of \"on|off|reboot|status\". Defaults to \"status\"."
	print "    -h : Print this help message."
	print "    -l : The username for the XenServer host."
	print "    -p : The password for the XenServer host."
	print "    -s : The URL of the web interface on the XenServer host."
	print "    -u : The UUID of the virtual machine to fence or query. Defaults to the empty string which will return"
	print "         the status of all hosts when action is set to \"status\". If the action is set to \"on|off|reboot\""
	print "         then the UUID must be specified."

# Process command line options and populate the config array
def process_opts():
	config = {
		"action"	: "status",
		"session_url"	: "",
		"session_user"	: "",
		"session_pass"	: "",
		"uuid"		: "",
		"verbose"	: False
		}
		
	try:
		opts, args = getopt.getopt(sys.argv[1:], "a:hl:s:p:u:v", ["help", "verbose", "action=", "session-url=", "login-name=", "password=", "uuid="])
	except getopt.GetoptError, err:
		# We got an unrecognised option, so print he help message and exit
		print str(err)
		usage()
		sys.exit(1)

	for opt, arg in opts:
		if opt in ("-v", "--verbose"):
			config["verbose"] = True
		elif opt in ("-a", "--action"):
			if arg in ("on", "poweron", "powerup"):
				config["action"] = "on"
			elif arg in ("off", "poweroff", "powerdown"):
				config["action"] = "off"
			elif arg in ("reboot", "reset"):
				config["action"] = "reboot"
			elif arg in ("status", "powerstatus"):
				config["action"] = "status"
		elif opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-s", "--session-url"):
			config["session_url"] = arg
		elif opt in ("-l", "--login-name"):
			config["session_user"] = arg
		elif opt in ("-p", "--password"):
			config["session_pass"] = arg
		elif opt in ("-u", "--uuid"):
			config["uuid"] = arg
		else:
			assert False, "unhandled option"

	if( config["session_url"] == "" or config["session_user"] == "" or config["session_pass"] == "" ):
		print "You must specify the session url, username and password.";
		usage();
		sys.exit(2);

	return config

# Print the power status of a VM. If no UUID is given, then all VM's are queried
def get_power_status(session, uuid = ""):
	try:
		if( uuid == "" ):
			vms = session.xenapi.VM.get_all()
		else:
			vms = [session.xenapi.VM.get_by_uuid(uuid)]
		for vm in vms:
			record = session.xenapi.VM.get_record(vm);
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				name = record["name_label"]
				print "UUID:", record["uuid"], "NAME:", name, "POWER STATUS:", record["power_state"]
	except Exception, exn:
		print str(exn);

def set_power_status(session, uuid, action):
	if( uuid == "" ):
		return;
	
	try:
		vm = session.xenapi.VM.get_by_uuid(uuid)
		record = session.xenapi.VM.get_record(vm);
		if not(record["is_a_template"]) and not(record["is_control_domain"]):
			if( action == "on" ):
				session.xenapi.VM.start(vm, False, True)
			elif( action == "off" ):
				session.xenapi.VM.hard_shutdown(vm)
			elif( action == "reboot" ):
				session.xenapi.VM.hard_reboot(vm)
	except Exception, exn:
		print str(exn);
	
def main():

	config = process_opts();
	
	session = session_start(config["session_url"]);
	session_login(session, config["session_user"], config["session_pass"]);

	if( config["action"] == "status" ):
		get_power_status(session, config["uuid"])
	else:
		if( config["verbose"] ):
			print "Power status before action"
			get_power_status(session, config["uuid"])

		set_power_status(session, config["uuid"], config["action"])

		if( config["verbose"] ):
			print "Power status after action"
			get_power_status(session, config["uuid"])

# Function to initiate the session with the XenServer system
def session_start(url):
	try:
		session = XenAPI.Session(url);
	except Exception, exn:
		print str(exn);
		sys.exit(3);
	return session;

def session_login(session, username, password):
	try:
		session.xenapi.login_with_password(username, password);
	except Exception, exn:
		print str(exn);
		sys.exit(3);

if __name__ == "__main__":
	main()

# vim:set ts=4 sw=4
