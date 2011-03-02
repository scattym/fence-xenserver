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
	print "    -a : Specifies the action to perfom. Can be any of \"on|off|reboot|status|list\". Defaults to \"status\"."
	print "    -h : Print this help message."
	print "    -l : The username for the XenServer host."
	print "    -p : The password for the XenServer host."
	print "    -s : The URL of the web interface on the XenServer host."
	print "    -U : The UUID of the virtual machine to fence or query. Defaults to the empty string which will return"
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
		"name"		: "",
		"verbose"	: False
		}
		
	# If we have at least one argument then we want to parse the command line using getopts
	if len(sys.argv) > 1:
		try:
			opts, args = getopt.getopt(sys.argv[1:], "a:hl:n:s:p:U:v", ["help", "verbose", "action=", "session-url=", "login-name=", "name=", "password=", "uuid="])
		except getopt.GetoptError, err:
			# We got an unrecognised option, so print he help message and exit
			print str(err)
			usage()
			sys.exit(1)
	
		for opt, arg in opts:
			if opt in ("-v", "--verbose"):
				config["verbose"] = True
			elif opt in ("-a", "--action"):
				config["action"] = clean_action(arg)
			elif opt in ("-h", "--help"):
				usage()
				sys.exit()
			elif opt in ("-s", "--session-url"):
				config["session_url"] = arg
			elif opt in ("-l", "--login-name"):
				config["session_user"] = arg
			elif opt in ("-n", "--name"):
				config["name"] = arg
			elif opt in ("-p", "--password"):
				config["session_pass"] = arg
			elif opt in ("-U", "--uuid"):
				config["uuid"] = arg.lower()
			else:
				assert False, "unhandled option"
	# Otherwise process stdin for parameters. This is to handle the Red Hat clustering
	# mechanism where by fenced passes in name/value pairs instead of using command line
	# options.
	else:
	
		for line in sys.stdin.readlines():
			line = line.strip()
			if ((line.startswith("#")) or (len(line) == 0)):
				continue
			(name, value) = (line + "=").split("=", 1)
			value = value[:-1]
	
			name = clean_param_name(name)
	
			if name == "action":
				value = clean_action(value)

			if name in config:
				config[name] = value
			else:
				sys.stderr.write("Parse error: Ignoring unknown option '"+line+"'\n")
	
	if( config["session_url"] == "" or config["session_user"] == "" or config["session_pass"] == "" ):
		print "You must specify the session url, username and password.";
		usage();
		sys.exit(2);

	return config

# why, well just to be nice. Given an action will return the corresponding
# value that the rest of the script uses.
def clean_action(action):
	if action.lower() in ("on", "poweron", "powerup"):
		return "on"
	elif action.lower() in ("off", "poweroff", "powerdown"):
		return "off"
	elif action.lower() in ("reboot", "reset", "restart"):
		return "reboot"
	elif action.lower() in ("status", "powerstatus", "list"):
		return "status"
	else:
		print "Bad action", action
		usage()
		exit(4)

# why, well just to be nice. Given a parameter will return the corresponding
# value that the rest of the script uses.
def clean_param_name(name):
	if name.lower() in ("action", "operation", "op"):
		return "action"
	elif name.lower() in ("session_user", "login", "login-name", "login_name", "user", "username", "session-user"):
		return "session_user"
	elif name.lower() in ("session_pass", "pass", "passwd", "password", "session-pass"):
		return "session_pass"
	elif name.lower() in ("session_url", "url", "session-url"):
		return "session_url"
	else:
		# we should never get here as getopt should handle the checking of this input.
		print "Bad parameter specified", name
		usage()
		exit(5)
	
# Print the power status of a VM. If no UUID is given, then all VM's are queried
def get_power_status(session, uuid = "", name = ""):
	try:
		# If the UUID hasn't been set, then output the status of all
		# valid virtual machines.
		if( len(uuid) > 0 ):
			vms = [session.xenapi.VM.get_by_uuid(uuid)]
		elif( len(name) > 0 ):
			vms = session.xenapi.VM.get_by_name_label(name)
		else:
			vms = session.xenapi.VM.get_all()

		for vm in vms:
			record = session.xenapi.VM.get_record(vm);
			# We only want to print out the status for actual virtual machines. The above get_all function
			# returns any templates and also the control domain. This is one of the reasons the process
			# takes such a long time to list all VM's. Hopefully there is a way to filter this in the
			# request packet in the future.
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				name = record["name_label"]
				print "UUID:", record["uuid"], "NAME:", name, "POWER STATUS:", record["power_state"]
	except Exception, exn:
		print str(exn);

def set_power_status(session, uuid, name, action):
	try:
		vm = None
		if( len(uuid) > 0 ):
			vm = session.xenapi.VM.get_by_uuid(uuid)
		elif( len(name) > 0 ):
			vm_arr = session.xenapi.VM.get_by_name_label(name)
			if( len(vm_arr) == 1 ):
				vm = vm_arr[0]
			else
				raise Exception("Multiple VM's have that name. Use UUID instead.")

		if( vm != None ):
			record = session.xenapi.VM.get_record(vm);
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				if( action == "on" ):
					session.xenapi.VM.start(vm, False, True)
				elif( action == "off" ):
					session.xenapi.VM.hard_shutdown(vm)
				elif( action == "reboot" ):
					session.xenapi.VM.hard_reboot(vm)
				else:
					raise Exception("Bad power status");
	except Exception, exn:
		print str(exn);
	
def main():

	config = process_opts();
	
	session = session_start(config["session_url"]);
	session_login(session, config["session_user"], config["session_pass"]);

	if( config["action"] == "status" ):
		get_power_status(session, config["uuid"], config["name"])
	else:
		if( config["verbose"] ):
			print "Power status before action"
			get_power_status(session, config["uuid"])

		set_power_status(session, config["uuid"], config["name"], config["action"])

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
