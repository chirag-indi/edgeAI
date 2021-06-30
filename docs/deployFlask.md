# Deploying a simple Flask application

The basic functionality of the application is to accept a request initiated in any of the pods and take a random walk through the remaining active pods dynamically fetching and using the flannel IP associated with the each of the pods.

The code is currently in the [repo](www.github.com).
## Building the Multiarch docker Image

A multiarchitecture Docker image facilitates the use of edge IoT devices to run the Flask server.
This is done using Docker Buildx which is a CLI plugin that extends the docker command and is designed to work well for building for multiple platforms and not only for the architecture and operating system that the user invoking the build happens to run.

### Create a new builder instance and update the current configuration

```
$ docker buildx create --name mybuilder
$ docker buildx use mybuilder
$ docker buildx inspect --bootstrap
```
### Install the multiarch emulator docker support

```
$ docker run --privileged --rm tonistiigi/binfmt --install all
```
Change directory into the folder with the Flask application and build and push the Dockerfile with support to amd64 and arm64.

```
$ cd /path/to/folder
$ docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t chiragindi/d2iedgeai:latest --push .
```

## Creating the deployments and services in Kubernetes

The following yaml file is saved into a file on the kuberenets cluster.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: d2iedgeai1
  name: d2iedgeai1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: d2iedgeai1
  template:
    metadata:
      labels:
        app: d2iedgeai1
    spec:
      containers:
      - image: chiragindi/d2iedgeai
        name: d2iedgeai1
        imagePullPolicy: Always
        ports:
        - containerPort: 12000
        env:
          - name: DEBUG
            value: "True"
          - name: NODE_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
      restartPolicy: Always
      nodeSelector:
        nodenumber: one
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: d2iedgeai1
  name: d2iedgeai1
spec: 
  type: NodePort
  selector: 
    app: d2iedgeai1
  ports:
  - port: 12000
    targetPort: 30001
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: d2iedgeai2
  name: d2iedgeai2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: d2iedgeai2
  template:
    metadata:
      labels:
        app: d2iedgeai2
    spec:
      containers:
      - image: chiragindi/d2iedgeai
        name: d2iedgeai2
        imagePullPolicy: Always
        ports:
        - containerPort: 12000
        env:
          - name: DEBUG
            value: "True"
          - name: NODE_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
      restartPolicy: Always
      nodeSelector:
        nodenumber: two
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: d2iedgeai2
  name: d2iedgeai2
spec: 
  type: NodePort
  selector: 
    app: d2iedgeai2
  ports:
  - port: 12000
    targetPort: 30002
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: d2iedgeai3
  name: d2iedgeai3
spec:
  replicas: 1
  selector:
    matchLabels:
      app: d2iedgeai3
  template:
    metadata:
      labels:
        app: d2iedgeai3
    spec:
      containers:
      - image: chiragindi/d2iedgeai
        name: d2iedgeai3
        imagePullPolicy: Always
        ports:
        - containerPort: 12000
        env:
          - name: DEBUG
            value: "True"
          - name: NODE_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
      restartPolicy: Always
      nodeSelector:
        nodenumber: three
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: d2iedgeai3
  name: d2iedgeai3
spec: 
  type: NodePort
  selector: 
    app: d2iedgeai3
  ports:
  - port: 12000
    targetPort: 30003
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: fabric8-rbac
subjects:
  - kind: ServiceAccount
    # Reference to upper's `metadata.name`
    name: default
    # Reference to upper's `metadata.namespace`
    namespace: default
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

The following command is then run to create the above mentioned resources. The RBAC is required for the kubernetes Python API to work. 

```
# kubectl apply -f config.yaml
```


