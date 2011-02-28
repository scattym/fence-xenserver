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

from fencing import *
import XenAPI

EC_BAD_SESSION 		= 1
# Find the status of the port given in the -U flag of options.
def get_power_fn(session, options):
	#uuid = options["-U"].lower()
	try:
		# Get a reference to the vm specified in the UUID or vm_name parameter
		vm = return_vm_reference(session, options)
		# Query the VM for its' associated parameters
		record = session.xenapi.VM.get_record(vm);
		# Check that we are not trying to manipulate a template or a control
		# domain as they show up as VM's with specific properties.
		if not(record["is_a_template"]) and not(record["is_control_domain"]):
			status = record["power_state"]
			print "UUID:", record["uuid"], "NAME:", record["name_label"], "POWER STATUS:", record["power_state"]
			# Note that the VM can be in the following states (from the XenAPI document)
			# Halted: VM is offline and not using any resources.
			# Paused: All resources have been allocated but the VM itself is paused and its vCPUs are not running
			# Running: Running
			# Paused: VM state has been saved to disk and it is nolonger running. Note that disks remain in-Use while
			# We want to make sure that we only return the status "off" if the machine is actually halted as the status
			# is checked before a fencing action. Only when the machine is Halted is it not consuming resources which
			# may include whatever you are trying to protect with this fencing action.
			return (status=="Halted" and "off" or "on")
	except Exception, exn:
		print str(exn)

	return "Error"

# Set the state of the port given in the -U flag of options.
def set_power_fn(session, options):
	uuid = options["-U"].lower()
	action = options["-o"].lower()
	
	try:
		# Get a reference to the vm specified in the UUID or vm_name parameter
		vm = return_vm_reference(session, options)
		# Query the VM for its' associated parameters
		record = session.xenapi.VM.get_record(vm)
		# Check that we are not trying to manipulate a template or a control
		# domain as they show up as VM's with specific properties.
		if not(record["is_a_template"]) and not(record["is_control_domain"]):
			if( action == "on" ):
				# Start the VM 
				session.xenapi.VM.start(vm, False, True)
			elif( action == "off" ):
				# Force shutdown the VM
				session.xenapi.VM.hard_shutdown(vm)
			elif( action == "reboot" ):
				# Force reboot the VM
				session.xenapi.VM.hard_reboot(vm)
	except Exception, exn:
		print str(exn);

# Function to populate an array of virtual machines and their status
def get_outlet_list(session, options):
	result = {}

	try:
		# Return an array of all the VM's on the host
		vms = session.xenapi.VM.get_all()
		for vm in vms:
			# Query the VM for its' associated parameters
			record = session.xenapi.VM.get_record(vm);
			# Check that we are not trying to manipulate a template or a control
			# domain as they show up as VM's with specific properties.
			if not(record["is_a_template"]) and not(record["is_control_domain"]):
				name = record["name_label"]
				uuid = record["uuid"]
				status = record["power_state"]
				result[uuid] = (name, status)
				print "UUID:", record["uuid"], "NAME:", name, "POWER STATUS:", record["power_state"]
	except Exception, exn:
		print str(exn);

	return result

# Function to initiate the XenServer session via the XenAPI library.
def connect_and_login(options):
	url = options["-s"]
	username = options["-l"]
	password = options["-p"]

	try:
		# Create the XML RPC session to the specified URL.
		session = XenAPI.Session(url);
		# Login using the supplied credentials.
		session.xenapi.login_with_password(username, password);
	except Exception, exn:
		print str(exn);
		# http://sources.redhat.com/cluster/wiki/FenceAgentAPI says that for no connectivity
		# the exit value should be 1. It doesn't say anything about failed logins, so 
		# until I hear otherwise it is best to keep this exit the same to make sure that
		# anything calling this script (that uses the same information in the web page
		# above) knows that this is an error condition, not a msg signifying a down port.
		sys.exit(EC_BAD_SESSION); 
	return session;

# return a reference to the VM by either using the UUID or the vm_name. If the UUID is set then
# this is tried first as this is the only properly unique identifier.
# Exceptions are not handled in this function, code that calls this must be ready to handle them.
def return_vm_reference(session, options):
	# Case where the UUID has been specified
	if options.has_key("-U"):
		uuid = options["-U"].lower()
		return session.xenapi.VM.get_by_uuid(uuid)

	# Case where the vm_name has been specified
	if options.has_key("-n"):
		vm_name = options["-n"]
		vm_arr = session.xenapi.VM.get_by_name_label(vm_name)
		# Need to make sure that we only have one result as the vm_name may
		# not be unique. Average case, so do it first.
		if len(vm_arr) == 1:
			return vm_arr[0]
		else:
			# TODO: Need to either fail usage or raise exception
			# at least say something like none or multiple vms found
			# with that name.
			# if len(vm_arr) == 0:
			#	no vm's found
			# else:
			# 	multiple vms found with the same name, use uuid instead
			return None

def main():

	device_opt = [ "help", "version", "agent", "quiet", "verbose", "debug", "action",
			"login", "passwd", "passwd_script", "vm_name", "test", "separator",
			"no_login", "no_password", "power_timeout", "shell_timeout",
			"login_timeout", "power_wait", "session_url", "uuid" ]

	atexit.register(atexit_handler)

	options=process_input(device_opt)

	options = check_input(device_opt, options)

	docs = { }
	docs["shortdesc"] = "Fence agent for Citrix XenServer"
	docs["longdesc"] = "fence_cxs_redhat" 
	show_docs(options, docs)

	xenSession = connect_and_login(options)
	
	# Operate the fencing device
	result = fence_action(xenSession, options, set_power_fn, get_power_fn, get_outlet_list)

	sys.exit(result)

if __name__ == "__main__":
	main()
