# Prerequisites of the Server/Master Node

The Kubernetes cluster is running inside a docker container on an AMD64/x86_64 system. 
[Sysbox Runtime](https://github.com/nestybox/sysbox), a open-source container runtime is used enable the docker container to esentially act as an VM enabling us to run a Kubernetes Cluster inside the container.

## Installing docker with apt-get

```
#!/bin/sh
# https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88 | grep docker@docker.com || exit 1
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
sudo docker run --rm hello-world
```

## Installing using the latest Docker release

    $ curl -fsSL https://get.docker.com/ | sh

## Finishing installation

Optional - add $USER to docker group (make sure to log out and back in after)

    $ sudo groupadd docker
    $ sudo usermod -aG docker $USER
    $ sudo systemctl restart docker


Logout and login so that group changes are in effect.

## Host Requirements

The Linux host on which Sysbox runs must meet the following requirements:

1.  It must have one of the [supported Linux distros](../distro-compat.md).

2.  Systemd must be the system's process-manager (the default in the supported distros).

## Installing Sysbox

**NOTE**: if you have a prior version of Sysbox already installed, please
[uninstall it](#uninstalling-sysbox) first and then follow the installation
instructions below.

1.  Download the latest Sysbox package from the [release](https://github.com/nestybox/sysbox/releases) page.

2.  Verify that the checksum of the downloaded file fully matches the
    expected/published one. For example:

```console
$ shasum sysbox-ce_0.3.0-0.ubuntu-focal_amd64.deb
4850d18ed2af73f2819820cd8993f9cdc647cc79  sysbox-ce_0.3.0-0.ubuntu-focal_amd64.deb
```

3.  If Docker is running on the host, stop and remove all running Docker containers:

```console
$ docker rm $(docker ps -a -q) -f
```

(if an error is returned, it simply indicates that no existing containers were found).

This is necessary because the Sysbox installer may need to configure and restart
Docker (to make Docker aware of Sysbox). It's possible to avoid the Docker restart;
see [Installing Sysbox w/o Docker restart](#installing-sysbox-without-restarting-docker)
below for more on this.

4.  Install the Sysbox package and follow the installer instructions:

```console
$ sudo apt-get install ./sysbox-ce_0.3.0-0.ubuntu-focal_amd64.deb -y
```

5.  Verify that Sysbox's Systemd units have been properly installed, and
    associated daemons are properly running:

```console
$ sudo systemctl status sysbox -n20

● sysbox.service - Sysbox container runtime
     Loaded: loaded (/lib/systemd/system/sysbox.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2021-03-27 00:15:36 EDT; 20s ago
       Docs: https://github.com/nestybox/sysbox
   Main PID: 2305016 (sh)
      Tasks: 2 (limit: 9487)
     Memory: 792.0K
     CGroup: /system.slice/sysbox.service
             ├─2305016 /bin/sh -c /usr/bin/sysbox-runc --version && /usr/bin/sysbox-mgr --version && /usr/bin/sysbox-fs --version && /bin/sleep infinity
             └─2305039 /bin/sleep infinity

Mar 27 00:15:36 dev-vm1 systemd[1]: Started Sysbox container runtime.
Mar 27 00:15:36 dev-vm1 sh[2305018]: sysbox-runc
Mar 27 00:15:36 dev-vm1 sh[2305018]:         edition:         Community Edition (CE)
Mar 27 00:15:36 dev-vm1 sh[2305018]:         version:         0.3.0
Mar 27 00:15:36 dev-vm1 sh[2305018]:         commit:          df952e5276cb6e705e0be331e9a9fe88f372eab8
Mar 27 00:15:36 dev-vm1 sh[2305018]:         built at:         Sat Mar 27 01:34:12 UTC 2021
Mar 27 00:15:36 dev-vm1 sh[2305018]:         built by:         Rodny Molina
Mar 27 00:15:36 dev-vm1 sh[2305018]:         oci-specs:         1.0.2-dev
Mar 27 00:15:36 dev-vm1 sh[2305024]: sysbox-mgr
Mar 27 00:15:36 dev-vm1 sh[2305024]:         edition:         Community Edition (CE)
Mar 27 00:15:36 dev-vm1 sh[2305024]:         version:         0.3.0
Mar 27 00:15:36 dev-vm1 sh[2305024]:         commit:          6ae5668e797ee1bb88fd5f5ae663873a87541ecb
Mar 27 00:15:36 dev-vm1 sh[2305024]:         built at:         Sat Mar 27 01:34:41 UTC 2021
Mar 27 00:15:36 dev-vm1 sh[2305024]:         built by:         Rodny Molina
Mar 27 00:15:36 dev-vm1 sh[2305031]: sysbox-fs
Mar 27 00:15:36 dev-vm1 sh[2305031]:         edition:         Community Edition (CE)
Mar 27 00:15:36 dev-vm1 sh[2305031]:         version:         0.3.0
Mar 27 00:15:36 dev-vm1 sh[2305031]:         commit:          bb001b7fe2a0a234fe86ab20045677470239e248
Mar 27 00:15:36 dev-vm1 sh[2305031]:         built at:         Sat Mar 27 01:34:30 UTC 2021
Mar 27 00:15:36 dev-vm1 sh[2305031]:         built by:         Rodny Molina
$
```

This indicates all Sysbox components are running properly.

