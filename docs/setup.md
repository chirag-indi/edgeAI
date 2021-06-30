#Cluster Setup

Create a Docker network

```
$ sudo docker network create dkrnet
```

Use the -v Docker option to mount the configuration file and log directory.

You can start the container and bind to the dkrnet network as follows. Alternatively, you can replace dkrnet with host below to use Docker’s host networking - if you only run a single container in your host.

```
$ docker run -d -v /path/to/config-005.json:/etc/opt/evio/config.json -v /path/to/logs/005:/var/log/edge-vpnio/ --rm --privileged --name evio005-master --network dkrnet --runtime=sysbox-runc edgevpnio/evio-node:20.12.2 /sbin/init
```
Exec into the Docker container

```
$ docker exec -it evio005-master bash
```

Install Docker and the prerequisites in the Docker Conatiner

```
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
# echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
# apt update
# apt-get install apt-transport-https ca-certificates curl gnupg lsb-release ssh vim docker-ce docker-ce-cli containerd.io -y
```

Start the newly installed Docker service
```
# systemctl start docker
```

This project is using [K3S](https://k3s.io), a Kubernetes distribution built for IoT & Edge computing.

Install and start K3S with a single command after replacing the correct flannel interface.

```
# curl -sfL https://get.k3s.io | sh -s - --docker --flannel-iface appbrXXXXXX --write-kubeconfig-mode 644 --write-kubeconfig $HOME/.kube/config
```

If this has executed correctly, you should see some output similar to

```
[INFO]  Finding release for channel stable
[INFO]  Using v1.21.1+k3s1 as release
[INFO]  Downloading hash https://github.com/k3s-io/k3s/releases/download/v1.21.1+k3s1/sha256sum-amd64.txt
[INFO]  Downloading binary https://github.com/k3s-io/k3s/releases/download/v1.21.1+k3s1/k3s
[INFO]  Verifying binary download
[INFO]  Installing k3s to /usr/local/bin/k3s
[INFO]  Creating /usr/local/bin/kubectl symlink to k3s
[INFO]  Creating /usr/local/bin/crictl symlink to k3s
[INFO]  Skipping /usr/local/bin/ctr symlink to k3s, command exists in PATH at /usr/bin/ctr
[INFO]  Creating killall script /usr/local/bin/k3s-killall.sh
[INFO]  Creating uninstall script /usr/local/bin/k3s-uninstall.sh
[INFO]  env: Creating environment file /etc/systemd/system/k3s.service.env
[INFO]  systemd: Creating service file /etc/systemd/system/k3s.service
[INFO]  systemd: Enabling k3s unit
Created symlink /etc/systemd/system/multi-user.target.wants/k3s.service → /etc/systemd/system/k3s.service.
[INFO]  systemd: Starting k3s
```

Find out the node token of the k3s cluster. 

```
# cat /var/lib/rancher/k3s/server/node-token
K10973d9d8a2e95eb3fb473559cad8b414268gf266d0f000a045ecbbfe08fdf64d4::server:19e2c05131439792rb723801c54d2f78
```

Test if you are able to ping each of the nodes from the master node/docker container.

```
# ping 10.10.100.1
# ping 10.10.100.2
# ping 10.10.100.3
```

On each of the following nodes, execute the below command to join the k3s cluster after replacing the `K3S_URL`, `K3S_TOKEN` and `flannel-iface`

```
# curl -sfL https://get.k3s.io | K3S_URL=https://10.10.100.5:6443 K3S_TOKEN=K10973d9d8a2e95eb3fb473559cad8b414268gf266d0f000a045ecbbfe08fdf64d4::server:19e2c05131439792rb723801c54d2f78 sh -s - --docker --flannel-iface appbXXXXX
```


After the Jetson nodes join the K3S cluster, label them as workers and respective node numbers which is used in `nodeSelector` attribute.

```
# kubectl label node d2iedgeai node-role.kubernetes.io/worker=worker
# kubectl label node d2iedgeai2 node-role.kubernetes.io/worker=worker
# kubectl label node d2iedgeai3-desktop node-role.kubernetes.io/worker=worker
# kubectl label nodes d2iedgeai nodenumber=one
# kubectl label nodes d2iedgeai2 nodenumber=two
# kubectl label nodes d2iedgeai3-desktop nodenumber=three
```

Confirm all the nodes have joined the cluster and are in Ready status.

```
# kubectl get nodes -o wide
NAME                 STATUS   ROLES                  AGE   VERSION        INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
d2iedgeai2           Ready    worker                 10h   v1.21.1+k3s1   10.10.100.2   <none>        Ubuntu 18.04.5 LTS   4.9.201+           docker://19.3.6
d2iedgeai3-desktop   Ready    worker                 10h   v1.21.1+k3s1   10.10.100.3   <none>        Ubuntu 18.04.5 LTS   4.9.201+           docker://19.3.6
d2iedgeai            Ready    worker                 10h   v1.21.1+k3s1   10.10.100.1   <none>        Ubuntu 18.04.5 LTS   4.9.201+           docker://19.3.6
5f632c8fe254         Ready    control-plane,master   11h   v1.21.1+k3s1   10.10.100.5   <none>        Ubuntu 18.04.1 LTS   5.8.0-55-generic   docker://20.10.7
```

The current cluster setup is made of 4 nodes in total. The main docker container runs on the server as the master/control plane, and the 3 Jetsons are worker nodes.
