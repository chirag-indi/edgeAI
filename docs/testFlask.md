# Testing the Flask application

Once the `kubectl apply` command has been run, you should three deployments, services and pod started.

```
# kubectl get pods -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE                 NOMINATED NODE   READINESS GATES
d2iedgeai3-6f674fb4fd-8796p   1/1     Running   0          12h   10.42.1.30   d2iedgeai3-desktop   <none>           <none>
d2iedgeai2-5db5448dd6-gn2xx   1/1     Running   0          12h   10.42.2.28   d2iedgeai2           <none>           <none>
d2iedgeai1-89d898b8d-6tv7j    1/1     Running   0          12h   10.42.3.31   d2iedgeai            <none>           <none>
```

As you can see, the three pods are running on differnt nodes.

To test the following application, select one of the pod IPs and run a `curl`. This should display the currently active pods which have IPs assigned.

```
# curl -X POST 10.42.2.28:12000/
{
  "10.42.1.30": "d2iedgeai3-6f674fb4fd-8796p", 
  "10.42.2.28": "d2iedgeai2-5db5448dd6-gn2xx", 
  "10.42.3.31": "d2iedgeai1-89d898b8d-6tv7j"
}
```

Similarly for taking a random walk between the pods

```
# curl 10.42.3.31:12000/start
[
  {
    "node_ip": "10.42.3.31", 
    "time": "06:38:58:880515"
  }, 
  {
    "node_ip": "10.42.2.28", 
    "time": "06:38:58:944868"
  }, 
  {
    "node_ip": "10.42.1.30", 
    "time": "06:38:58:965605"
  }
]
```

