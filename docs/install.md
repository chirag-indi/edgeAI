# Install the VPN

You need to add the evio repository to your node - this step needs only be done once for a host:

    sudo bash
    # echo "deb [trusted=yes] https://apt.fury.io/evio/ /" > /etc/apt/sources.list.d/fury.list
    # apt update

To install the package:

    # apt install evio

If the installation fails due to the libffi-dev dependence, you might need to add that manually:

    # apt-get install libffi-dev
    # apt install evio

### Edit Configuration File

After installation, but before starting, configure your node by editing /etc/opt/evio/config.json. The easiest way to get started with a working configuration is to request a trial account. You can also use the template from this page and add XMPP credentials, setting the IP address, and applying other configurations as needed

### Run Service and disable multicast

Replace appbrXXXXX with the name of your Evio bridge in the command below to disable multicast:

sudo systemctl start evio
sudo ip link set appbrXXXXX multicast off

Additionally, use systemctl to start/stop/restart/status evio.

### Dependencies

The installer has dependencies on, and will install python3 (>=3.8), python3-dev (>=3.8), python3-pip, iproute2, bridge-utils.

### Related Files and Directories

By default, the following files and directories are created:

* /opt/evio/tincan
* /opt/evio/controller/
* /etc/opt/evio/config.json

### Disabling or removing the software

To disable Start on Boot:

    sudo systemctl disable evio

To remove the package:

    sudo apt remove -y evio