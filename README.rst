Installer notes
---------------

This branch (https://github.com/NetApp/cinder/tree/stable/juno-cdot-fc-support)
contains a backport of the Cinder FibreChannel driver for NetApp Clustered Data
ONTAP (cDOT) from the OpenStack 'Kilo' release that has been tested with
OpenStack 'Juno'. All other NetApp drivers for Cinder have been removed from or
disabled in this branch.

To use this NetApp cDOT FibreChannel driver with OpenStack 'Juno', install Juno
as usual, replace the NetApp driver directory (cinder/volume/drivers/netapp)
with the contents from this branch on each host where the Cinder volume service
is enabled, and restart the Cinder volume service.

Instructions for configuring the NetApp cDOT FibreChannel driver may be found
in NetApp's `Kilo OpenStack Deployment and Operations Guide
<http://netapp.github.io/openstack-deploy-ops-guide/kilo>`_.