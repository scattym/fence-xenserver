Scripts to fence domU virtual machines hosted on a Citrix XenServer or Xen Cloud Platform (XCP) dom0 physical machine.

There are two scripts at the moment that are capable of fencing a virtual machine that is running on a XenServer host. This script is needed if you are using some sort of shared access device like an iSCSI device.

The Red Hat version of the fencing script (fence\_cxs\_redhat.py) is now ready and fully functional. It is able to fence a VM by UUID or by VM name. It can work on the command line, or via parameters supplied to stdin meaning that it is compatible with the fencing daemon that the Red Hat clustering suite uses (fenced and fence\_node). To use the Red Hat style script, you need to use the fencing.py script supplied in this repository as I have had to make a number of changes to add the required functionality. These changes will hopefully be adopted by the fencing agents project in the future. Hopefully this script will be too :) I am already talking with some people in Red Hat, so this seems like it might be quite possible. See the INSTALL file, in the repository or download package, for a quick guide to running this on your system.

There is also a standalone script (fence\_cxs.py) that does not use the fencing library developed by Red Hat. Both command line and stdin modes work for this script (and thus should work with fenced) however there are some features currently missing from this version (ability to retry, checking status before fencing, etc). If my changes to the fencing.py script gets adopted by heartbeat/pacemaker, then this script will most likely go away. I will only keep developing it if a need arises in these other projects.

Have tested these on Citrix XenServer 5.6.1-fp1, please let me know if it does or does not fence properly on any other versions. As the XenAPI is also used in Xen Cloud Platform, these scripts should be compatible. Again, please let me know if this does work on XCP.

Update: This script has been tested on XCP 0.1.1 and confirmed to work. Thanks to Anatoliy.

**THIS SCRIPT HAS NOW BEEN ADDED TO THE REDHAT FENCE AGENTS REPOSITORY**

http://git.fedorahosted.org/git/?p=fence-agents.git

