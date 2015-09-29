# Introduction #

Installation on a linux system.


# Details #
There are two version of the script in the repository, a command line version and a Red Hat Cluster Suite compatible script. (I hope to eventually merge the two).

**1) Installation of the generic script fence\_cxs.py**

Two scripts are required for this fencing app to work. First the script itself (fence\_cxs.py) should be copied somewhere into your path. Either /usr/local/sbin or /usr/sbin are good choices.

You then need to put the XenAPI.py script (from http://community.citrix.com/display/xs/XenServer+XenAPI.py or in the SDK available from http://community.citrix.com/display/xs/XenServer+SDK) somewhere in your Python library path. Or simply put it in the same directory as the fence\_cxs.py script.

And that should be it. Run _fence\_cxs.py -h_ to see the available options.

**2) Installation of the Red Hat style script fence\_cxs\_redhat.py**

Three scripts are required for this script to run. First the script itself (fence\_cxs\_redhat.py) should be copied somewhere into your path. Either /usr/local/sbin or /usr/sbin are good choices.

You then need to put the XenAPI.py script/library (from http://community.citrix.com/display/xs/XenServer+XenAPI.py or in the SDK available from http://community.citrix.com/display/xs/XenServer+SDK) somewhere in your Python library path. Or simply put it in the same directory as the fence\_cxs\_redhat.py script.

The final script/library is the fencing.py script that is available as one of the Red Hat Cluster rpms. I think it's part of the cman package. If you have installed Red Hat clustering, it is most likely already on your system.
UPDATE: I ended up having to update this script, so I have included it in the 0.3 version. The fencing.py library was not written by me, credit for that one goes to someone in Red Hat I think. Because I have made a couple of changes to this file, I have included it in the repository.

And that should be it. Run _fence\_cxs\_redhat.py -h_ to see the available options.