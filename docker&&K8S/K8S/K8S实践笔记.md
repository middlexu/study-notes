遇到了一个坑

```bash
[root@localhost k8s]# kubectl apply -f deployment_nginx.yml 
error: unable to recognize "deployment_nginx.yml": Get https://192.168.221.129:8443/api?timeout=32s: dial tcp 192.168.221.129:8443: connect: connection refused
```

原因是我关机重启了，K8S集群没有开启

```bash
[root@localhost k8s]# minikube start
* minikube v1.3.0 on Centos 7.6.1810
! Please don't run minikube as root or with 'sudo' privileges. It isn't necessary with virtualbox driver.
* Using image repository registry.cn-hangzhou.aliyuncs.com/google_containers
* Downloading VM boot image ...
    minikube-v1.3.0.iso.sha256: 65 B / 65 B [=====================] 100.00% 0s
    minikube-v1.3.0.iso: 131.07 MiB / 131.07 MiB [===============] 100.00% 16s
* 

! Ignoring --vm-driver=virtualbox, as the existing "minikube" VM was created using the none driver.
! To switch drivers, you may create a new VM using `minikube start -p <name> --vm-driver=virtualbox`
! Alternatively, you may delete the existing VM using `minikube delete -p minikube`
* 

* Starting existing none VM for "minikube" ...
* Waiting for the host to be provisioned ...
* Preparing Kubernetes v1.15.2 on Docker 19.03.1 ...
* Relaunching Kubernetes using kubeadm ... 
* Waiting for: apiserver proxy etcd scheduler controller dns
* Done! kubectl is now configured to use "minikube"
[root@localhost k8s]# kubectl get componentstatus
NAME                 STATUS    MESSAGE             ERROR
scheduler            Healthy   ok                  
controller-manager   Healthy   ok                  
etcd-0               Healthy   {"health":"true"} 
[root@localhost k8s]# kubectl cluster-info
```



### K8S集群

切换集群

```bash
[root@localhost k8s]# kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO   NAMESPACE
*         minikube   minikube   minikube   
[root@localhost k8s]# kubectl config use-context NAME
我这里只有一个minikube没法演示
```



```
停止集群
minikube stop
删除集群
minikube delete
开启集群
minikube start --vm-driver=none
```





发现了一个在线使用K8S的网站https://www.katacoda.com/courses/kubernetes/playground





### pod

pod_busybox.yml

```yml
apiVersion: v1
kind: Pod
metadata:
  name: busybox
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
```

pod_nginx.yml
```yml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
```





### deployment

比RC（ReplicationController）功能要强大一些，用来替代RC的



deployment_nginx.yml

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
```

```bash
[root@localhost k8s]# kubectl apply -f deployment_nginx.yml 
deployment.apps/nginx-deployment created
[root@localhost k8s]# kubectl get pods -o wide
NAME                                READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
nginx-deployment-7bffc778db-9nvbf   1/1     Running   0          30s   172.17.0.5   minikube   <none>           <none>
nginx-deployment-7bffc778db-hz2gn   1/1     Running   0          30s   172.17.0.6   minikube   <none>           <none>
[root@localhost k8s]# curl 172.17.0.5:80 或者 curl 172.17.0.6:80 访问网站

```





### service

在容器内部，是可以通过curl service-name访问的

```bash
master $ kubectl run d1 --image httpd:alpine --port 80
master $ kubectl expose deployment d1 --target-port 80 --type NodePort
master $ kubectl run d2 --image nginx:alpine --port 80
master $ kubectl expose deployment d2 --target-port 80 --type NodePort
master $ kubectl exec d1-cc779c766-rpm8s -it sh
/usr/local/apache2 # apk add curl
/usr/local/apache2 # curl d2

出了容器是不行的
master $ curl d2
curl: (6) Could not resolve host: d2
```





#### LoadBalancer方式

service_lb_nginx.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: service-nginx
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
```

```bash
[root@localhost k8s]# kubectl apply -f service_lb_nginx.yml 
[root@localhost k8s]# kubectl get svc
NAME            TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
kubernetes      ClusterIP      10.96.0.1      <none>        443/TCP          15h
service-nginx   LoadBalancer   10.96.179.68   <pending>     8080:31525/TCP   8s
[root@localhost k8s]# curl 10.96.179.68:8080
[root@localhost k8s]# curl 192.168.221.129:31525
以上两个都是可以访问的
```





或者用kubectl expose方式创建service。创建LoadBalancer型的svc (默认是ClusterIP类型)

```bash
[root@localhost k8s]# kubectl expose deployment nginx-deployment --type=LoadBalancer
service/pod-nginx exposed
```





#### ClusterIP方式

kubectl expose方式

```bash
[root@localhost k8s]# kubectl expose deployment nginx-deployment --port 8888 --target-port=80         //注意这里的nginx-deployment指的是deployment的名字，同时生成的service也是这个名字
[root@localhost k8s]# kubectl get services
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
kubernetes         ClusterIP   10.96.0.1       <none>        443/TCP    122m
nginx-deployment   ClusterIP   10.105.43.247   <none>        8888/TCP   31s
[root@localhost k8s]# curl 10.105.43.247:8888
通过172.17.0.5:8888访问是失败的
[root@localhost k8s]# curl 172.17.0.5:8888  //connection refused
[root@localhost k8s]# kubectl delete service nginx-deployment  //删除service
```



service_nginx.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: service-nginx
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 80
```

```bash
[root@localhost k8s]# kubectl get service
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
kubernetes      ClusterIP   10.96.0.1       <none>        443/TCP    140m
service-nginx   ClusterIP   10.101.239.50   <none>        8080/TCP   13s
[root@localhost k8s]# curl 10.101.239.50:8080
[root@localhost k8s]# curl 172.17.0.5:8080  //connection refused
```





#### Nodeport方式

service_nodeport_nginx.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: service-nginx
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 888           #service的端口
    targetPort: 80      #pod的端口
    #nodePort: 30000    范围30000-32767，指定主机暴露的端口
```

```bash
[root@localhost k8s]# kubectl apply -f service_nodeport_nginx.yml 
service/service-nginx configured
[root@localhost k8s]# kubectl get service
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
kubernetes      ClusterIP   10.96.0.1       <none>        443/TCP         148m
service-nginx   NodePort    10.101.239.50   <none>        888:31480/TCP   7m49s
[root@localhost k8s]# curl 10.101.239.50:888
[root@localhost k8s]# curl 172.17.0.5:888   //connection refused
```

但是我在主机上是可以192.168.221.129:31480访问的。前面那个是虚拟机的ip地址

```
$ curl 192.168.221.129:31480
```

如果前面的nodePort注释放开，就是访问30000端口





### ingress

**容器外部访问容器内部（通过域名访问）**



```bash
kubectl run d1 --image httpd:alpine --port 80
kubectl expose deployment d1 --target-port 80 --type NodePort #默认的port也是80
kubectl run d2 --image nginx:alpine --port 80
kubectl expose deployment d2 --target-port 80 --type NodePort
```



ingress-deployment.yml

```yml
apiVersion: v1
kind: Namespace
metadata:
  name: nginx-ingress
---
apiVersion: v1
kind: Secret
metadata:
  name: default-server-secret
  namespace: nginx-ingress
type: Opaque
data:
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUN2akNDQWFZQ0NRREFPRjl0THNhWFhEQU5CZ2txaGtpRzl3MEJBUXNGQURBaE1SOHdIUVlEVlFRRERCWk8KUjBsT1dFbHVaM0psYzNORGIyNTBjbTlzYkdWeU1CNFhEVEU0TURreE1qRTRNRE16TlZvWERUSXpNRGt4TVRFNApNRE16TlZvd0lURWZNQjBHQTFVRUF3d1dUa2RKVGxoSmJtZHlaWE56UTI5dWRISnZiR3hsY2pDQ0FTSXdEUVlKCktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQUwvN2hIUEtFWGRMdjNyaUM3QlBrMTNpWkt5eTlyQ08KR2xZUXYyK2EzUDF0azIrS3YwVGF5aGRCbDRrcnNUcTZzZm8vWUk1Y2Vhbkw4WGM3U1pyQkVRYm9EN2REbWs1Qgo4eDZLS2xHWU5IWlg0Rm5UZ0VPaStlM2ptTFFxRlBSY1kzVnNPazFFeUZBL0JnWlJVbkNHZUtGeERSN0tQdGhyCmtqSXVuektURXUyaDU4Tlp0S21ScUJHdDEwcTNRYzhZT3ExM2FnbmovUWRjc0ZYYTJnMjB1K1lYZDdoZ3krZksKWk4vVUkxQUQ0YzZyM1lma1ZWUmVHd1lxQVp1WXN2V0RKbW1GNWRwdEMzN011cDBPRUxVTExSakZJOTZXNXIwSAo1TmdPc25NWFJNV1hYVlpiNWRxT3R0SmRtS3FhZ25TZ1JQQVpQN2MwQjFQU2FqYzZjNGZRVXpNQ0F3RUFBVEFOCkJna3Foa2lHOXcwQkFRc0ZBQU9DQVFFQWpLb2tRdGRPcEsrTzhibWVPc3lySmdJSXJycVFVY2ZOUitjb0hZVUoKdGhrYnhITFMzR3VBTWI5dm15VExPY2xxeC9aYzJPblEwMEJCLzlTb0swcitFZ1U2UlVrRWtWcitTTFA3NTdUWgozZWI4dmdPdEduMS9ienM3bzNBaS9kclkrcUI5Q2k1S3lPc3FHTG1US2xFaUtOYkcyR1ZyTWxjS0ZYQU80YTY3Cklnc1hzYktNbTQwV1U3cG9mcGltU1ZmaXFSdkV5YmN3N0NYODF6cFErUyt1eHRYK2VBZ3V0NHh3VlI5d2IyVXYKelhuZk9HbWhWNThDd1dIQnNKa0kxNXhaa2VUWXdSN0diaEFMSkZUUkk3dkhvQXprTWIzbjAxQjQyWjNrN3RXNQpJUDFmTlpIOFUvOWxiUHNoT21FRFZkdjF5ZytVRVJxbStGSis2R0oxeFJGcGZnPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo=
  tls.key: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcEFJQkFBS0NBUUVBdi91RWM4b1JkMHUvZXVJTHNFK1RYZUprckxMMnNJNGFWaEMvYjVyYy9XMlRiNHEvClJOcktGMEdYaVN1eE9ycXgrajlnamx4NXFjdnhkenRKbXNFUkJ1Z1B0ME9hVGtIekhvb3FVWmcwZGxmZ1dkT0EKUTZMNTdlT1l0Q29VOUZ4amRXdzZUVVRJVUQ4R0JsRlNjSVo0b1hFTkhzbysyR3VTTWk2Zk1wTVM3YUhudzFtMApxWkdvRWEzWFNyZEJ6eGc2clhkcUNlUDlCMXl3VmRyYURiUzc1aGQzdUdETDU4cGszOVFqVUFQaHpxdmRoK1JWClZGNGJCaW9CbTVpeTlZTW1hWVhsMm0wTGZzeTZuUTRRdFFzdEdNVWozcGJtdlFmazJBNnljeGRFeFpkZFZsdmwKMm82MjBsMllxcHFDZEtCRThCay90elFIVTlKcU56cHpoOUJUTXdJREFRQUJBb0lCQVFDZklHbXowOHhRVmorNwpLZnZJUXQwQ0YzR2MxNld6eDhVNml4MHg4Mm15d1kxUUNlL3BzWE9LZlRxT1h1SENyUlp5TnUvZ2IvUUQ4bUFOCmxOMjRZTWl0TWRJODg5TEZoTkp3QU5OODJDeTczckM5bzVvUDlkazAvYzRIbjAzSkVYNzZ5QjgzQm9rR1FvYksKMjhMNk0rdHUzUmFqNjd6Vmc2d2szaEhrU0pXSzBwV1YrSjdrUkRWYmhDYUZhNk5nMUZNRWxhTlozVDhhUUtyQgpDUDNDeEFTdjYxWTk5TEI4KzNXWVFIK3NYaTVGM01pYVNBZ1BkQUk3WEh1dXFET1lvMU5PL0JoSGt1aVg2QnRtCnorNTZud2pZMy8yUytSRmNBc3JMTnIwMDJZZi9oY0IraVlDNzVWYmcydVd6WTY3TWdOTGQ5VW9RU3BDRkYrVm4KM0cyUnhybnhBb0dCQU40U3M0ZVlPU2huMVpQQjdhTUZsY0k2RHR2S2ErTGZTTXFyY2pOZjJlSEpZNnhubmxKdgpGenpGL2RiVWVTbWxSekR0WkdlcXZXaHFISy9iTjIyeWJhOU1WMDlRQ0JFTk5jNmtWajJTVHpUWkJVbEx4QzYrCk93Z0wyZHhKendWelU0VC84ajdHalRUN05BZVpFS2FvRHFyRG5BYWkyaW5oZU1JVWZHRXFGKzJyQW9HQkFOMVAKK0tZL0lsS3RWRzRKSklQNzBjUis3RmpyeXJpY05iWCtQVzUvOXFHaWxnY2grZ3l4b25BWlBpd2NpeDN3QVpGdwpaZC96ZFB2aTBkWEppc1BSZjRMazg5b2pCUmpiRmRmc2l5UmJYbyt3TFU4NUhRU2NGMnN5aUFPaTVBRHdVU0FkCm45YWFweUNweEFkREtERHdObit3ZFhtaTZ0OHRpSFRkK3RoVDhkaVpBb0dCQUt6Wis1bG9OOTBtYlF4VVh5YUwKMjFSUm9tMGJjcndsTmVCaWNFSmlzaEhYa2xpSVVxZ3hSZklNM2hhUVRUcklKZENFaHFsV01aV0xPb2I2NTNyZgo3aFlMSXM1ZUtka3o0aFRVdnpldm9TMHVXcm9CV2xOVHlGanIrSWhKZnZUc0hpOGdsU3FkbXgySkJhZUFVWUNXCndNdlQ4NmNLclNyNkQrZG8wS05FZzFsL0FvR0FlMkFVdHVFbFNqLzBmRzgrV3hHc1RFV1JqclRNUzRSUjhRWXQKeXdjdFA4aDZxTGxKUTRCWGxQU05rMXZLTmtOUkxIb2pZT2pCQTViYjhibXNVU1BlV09NNENoaFJ4QnlHbmR2eAphYkJDRkFwY0IvbEg4d1R0alVZYlN5T294ZGt5OEp0ek90ajJhS0FiZHd6NlArWDZDODhjZmxYVFo5MWpYL3RMCjF3TmRKS2tDZ1lCbyt0UzB5TzJ2SWFmK2UwSkN5TGhzVDQ5cTN3Zis2QWVqWGx2WDJ1VnRYejN5QTZnbXo5aCsKcDNlK2JMRUxwb3B0WFhNdUFRR0xhUkcrYlNNcjR5dERYbE5ZSndUeThXczNKY3dlSTdqZVp2b0ZpbmNvVlVIMwphdmxoTUVCRGYxSjltSDB5cDBwWUNaS2ROdHNvZEZtQktzVEtQMjJhTmtsVVhCS3gyZzR6cFE9PQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQo=
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nginx-ingress
  namespace: nginx-ingress
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: nginx-config
  namespace: nginx-ingress
data:
---
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: nginx-ingress
  namespace: nginx-ingress
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-ingress
  template:
    metadata:
      labels:
        app: nginx-ingress
    spec:
      serviceAccountName: nginx-ingress
      containers:
      - image: nginx/nginx-ingress:edge
        imagePullPolicy: Always
        name: nginx-ingress
        ports:
        - name: http
          containerPort: 80
        - name: https
          containerPort: 443
        env:
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        args:
          - -nginx-configmaps=$(POD_NAMESPACE)/nginx-config
          - -default-server-tls-secret=$(POD_NAMESPACE)/default-server-secret
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-ingress
  namespace: nginx-ingress
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  - port: 443
    targetPort: 443
    protocol: TCP
    name: https
  selector:
    app: nginx-ingress
  externalIPs:
    - 172.17.0.8           # 这个需要修改为本机ip
```

ingress-conf.yml

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: test-ng-ingress
spec:
  rules:
  - host: a.b.c
    http:
      paths:
      - backend:
          serviceName: d1
          servicePort: 80
  - host: a.b.d
    http:
      paths:
      - backend:
          serviceName: d2
          servicePort: 80
```





```bash
[root@localhost k8s]$ kubectl apply -f ingress-deployment.yml
namespace/nginx-ingress created
secret/default-server-secret created
serviceaccount/nginx-ingress created
configmap/nginx-config created
deployment.extensions/nginx-ingress created
service/nginx-ingress created
[root@localhost k8s]$ kubectl get deployment --all-namespaces
NAMESPACE       NAME            READY   UP-TO-DATE   AVAILABLE   AGE
kube-system     coredns         2/2     2            2           39m
nginx-ingress   nginx-ingress   1/1     1            1           5m24s
[root@localhost k8s]$ kubectl get svc  --all-namespaces
NAMESPACE       NAME            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
default         kubernetes      ClusterIP   10.96.0.1        <none>        443/TCP                      40m
kube-system     kube-dns        ClusterIP   10.96.0.10       <none>        53/UDP,53/TCP,9153/TCP       40m
nginx-ingress   nginx-ingress   NodePort    10.101.246.138   172.17.0.8    80:32142/TCP,443:31222/TCP   5m54s
[root@localhost k8s]$ kubectl apply -f ingress-conf.yml
ingress.extensions/test-ng-ingress created
[root@localhost k8s]$ kubectl  get  ingress --all-namespaces
NAMESPACE   NAME              HOSTS         ADDRESS   PORTS   AGE
default     test-ng-ingress   ng.test.com             80      4m1s
[root@localhost k8s]$ curl -H "Host:a.b.c" 172.17.0.8
<html><body><h1>It works!</h1></body></html>
[root@localhost k8s]$ curl -H "Host:a.b.d" 172.17.0.8
结果为nginx默认页面
```

以上是我在K8S online上的测验。但是我在minikube上测试`curl -H "Host:a.b.d" 192.168.221.129`是不行的





最后对外访问的路径变成了 k8s.xxx.com/service_name/service_method?params=xxx，这个路径可以通过k8s的ingress访问到配置的的nginx服务，然后通过nginx的配置，可以把原始的路径进行了处理，把请求变成service_name/service_method?params=xxx然后转发给后面的真实服务。





### 服务总结

service创建之后，之后创建的pod，里面env会含有service的信息

```bash
[root@localhost k8s]# kubectl exec pod-busybox env
```





**ClusterIP Service**

ClusterIP Service 是 Kubernetes 的默认服务。它给你一个集群内的服务，集群内的其它应用都可以访问该服务。集群外部无法访问它。

**LoadBlancer Service**

LoadBlancer Service 是 Kubernetes 结合云平台的组件，如国外 GCE、AWS、国内阿里云等等，使用它向使用的底层云平台申请创建负载均衡器来实现，有局限性，对于使用云平台的集群比较方便。

**NodePort Service**

NodePort Service 是在所有节点（虚拟机）上开放一个特定端口，然后通过将端口映射到具体某个服务上来实现服务暴漏，比较直观方便，但是对于集群来说，随着 Service 的不断增加，需要的端口越来越多，很容易出现端口冲突，而且不容易管理。当然对于小规模的集群服务，还是比较不错的。

**Ingress**

Ingress 使用开源的反向代理负载均衡器来实现对外暴漏服务，比如 Nginx、Apache、Haproxy等。Nginx Ingress 一般有三个组件组成：

- Nginx 反向代理负载均衡器

- Ingress Controller

  Ingress Controller 可以理解为控制器，它通过不断的跟 Kubernetes API 交互，实时获取后端 Service、Pod 等的变化，比如新增、删除等，然后结合 Ingress 定义的规则生成配置，然后动态更新上边的 Nginx 负载均衡器，并刷新使配置生效，来达到服务自动发现的作用。

- Ingress

  Ingress 则是定义规则，通过它定义某个域名的请求过来之后转发到集群中指定的 Service。它可以通过 Yaml 文件定义，可以给一个或多个 Service 定义一个或多个 Ingress 规则。

以上三者有机的协调配合起来，就可以完成 Kubernetes 集群服务的暴漏。



参考视频https://www.bilibili.com/video/av61990770






### 健康检查

**readinessProbe 和 livenessProbe**

<font color="red">需要健康检查完之后，才会对外提供服务</font>

ProbeType有三种：command, httpGet, tcpSocket. 具体使用方法看PPT



示例一

deployment_python_http_healthckeck.yml

```yml
apiVersion:  apps/v1
kind: Deployment
metadata:
  name: service-test
spec:
  replicas: 1
  selector:
    matchLabels:
      app: service_test_pod
  template:
    metadata:
      labels:
        app: service_test_pod
    spec:
      containers:
      - name: simple-http
        image: python:2.7
        imagePullPolicy: IfNotPresent
        command: ["/bin/bash"]
        args: ["-c", "echo \"<p>Hello from $(hostname)</p>\" > index.html; sleep 30; python -m SimpleHTTPServer 8080"]
        ports:
        - name: http
          containerPort: 8080
        readinessProbe:
          tcpSocket:
            port: 8080
          initialDelaySeconds: 35
          periodSeconds: 10
        livenessProbe:
          tcpSocket:
            port: 8080
          initialDelaySeconds: 40
          periodSeconds: 20
```

示例二

exec_liveness.yml

```yml
apiVersion: v1
kind: Pod
metadata:
  labels:
    test: liveness
  name: liveness-exec
spec:
  containers:
  - name: liveness
    image: k8s.gcr.io/busybox
    args:
    - /bin/sh
    - -c
    - touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 60000
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5
      periodSeconds: 5
```







### volumes

```yml
apiVersion: v1
kind: Pod
metadata:
  name: test-pd
spec:
  containers:
  - name: busybox1
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    volumeMounts:
    - mountPath: /test-pd
      name: test-volume
  - name: busybox2
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    volumeMounts:
    - mountPath: /test-pd
      name: test-volume
  volumes:
  - name: test-volume
    hostPath:
      # directory location on host
      path: /data
      # this field is optional
      type: Directory
```

hostPath挂载在本地





云环境操作

PVC（PersistentVolumeClaim） 创建 PV（PersistentVolume）

mysql-pvc.yml

```yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-volumeclaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

```bash
kubectl apply -f pvc-demo.yml
```

这时云服务商会创建一块20G的磁盘

msql.yml

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - image: mysql:5.6
          name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD     # root的密码设置，这种方式不好，最好用secret
              value: password
          ports:
            - containerPort: 3306
              name: mysql
          volumeMounts:
            - name: mysql-persistent-storage
              mountPath: /var/lib/mysql     # 这个是mysql的数据挂载目录
      volumes:
        - name: mysql-persistent-storage
          persistentVolumeClaim:
            claimName: mysql-volumeclaim
```

```bash
kubectl apply -f pvc-demo.yml
```





### secret

查看secret的创建方式(通常是创建generic类型的)

```bash
kubectl create secret generic --help
```

```bash
创建secret，(ssh-privatekey,id_rsa文件里的内容)(ssh-publickey,id_rsa.pub文件里的内容)
kubectl create secret generic my-secret --from-file=ssh-privatekey=id_rsa --from-file=ssh-publickey=id_rsa.pub

kubectl delete secret mysecret

创建secret，(key1,value1)(key2,value2)
kubectl create secret generic my-secret --from-literal=key1=value1 --from-literal=key2=value2
```

通过yml创建

```yml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  root-password: YWJjMTIz     # abc123的base64值（echo -n "abc123" | base64）
  no-root-password: YWJjMTIz
```

> echo -n "123"      -n表示不换行





使用(env方式)

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  labels:
    app: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - image: mysql:5.6
          name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-secret
                  key: root-password
          ports:
            - containerPort: 3306
              name: mysql
```

使用(volume方式)  

```yml
apiVersion: v1
kind: Pod
metadata:
  name: secret_busybox
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    volumeMounts:
      - name: secret_key
        mountPath: "/tmp/apikey"
        readOnly: true
  volumes:
  - name: secret_key
    secret:
      secretName: my-secret
```

将my-secret挂载到/tmp/apikey目录下，生成多个文件，key为文件名，value为文件内容





### configMap

使用方式和secret基本上是一样的

```bash
kubectl create configmap config-1 --from-literal=host=1.1.1.1 --from-literal=port=3000
```

通过yml创建

```yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config-1
  namespace: default
data:
  host: 1.1.1.1
  port: "3000"
```



使用（env方式）

```yml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-1
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    env:
      - name: HOST
        valueFrom:
          configMapKeyRef:
            name: config-1
            key: host
      - name: PORT
        valueFrom:
          configMapKeyRef:
            name: config-1
            key: port
```

使用（volume方式）

```yml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-2
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    volumeMounts:
      - name: config-volume
        mountPath: /etc/config
  volumes:
      - name: config-volume
        configMap:
          name: config-2
```





### 待补充

资源限制（CPU，内存）

部分内容来自https://www.bilibili.com/video/av49061801