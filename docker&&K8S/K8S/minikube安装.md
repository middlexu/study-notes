我的docker版本是18.09.3



```
curl -Lo minikube http://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/releases/v1.2.0/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
```

后来我docker版本19.03.1（当时最新）  这个装的是v1.3.0(当时最新)（都是去GitHub上release找最新）



```
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/v1.15.0/bin/linux/amd64/kubectl && chmod +x kubectl && sudo mv kubectl /usr/local/bin/
```

后来我docker版本19.03.1（当时最新）  这个装的是v1.16.0(当时最新)，这个出错了。最后1.15.2可以

如果下载不了https://blog.csdn.net/faryang/article/details/79427573



```
# linux 下独有，不依赖虚拟机启动
minikube start --vm-driver=none

主机装有虚拟机，可以直接
minikube start
```

可是我的阿里云报错了

[ERROR NumCPU]: the number of available CPUs 1 is less than the required 2

配置不够

最后还是在虚拟机上试了





```bash
[root@localhost ~]# kubectl version
Client Version: version.Info{Major:"1", Minor:"15", GitVersion:"v1.15.2", GitCommit:"f6278300bebbb750328ac16ee6dd3aa7d3549568", GitTreeState:"clean", BuildDate:"2019-08-05T09:23:26Z", GoVersion:"go1.12.5", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"15", GitVersion:"v1.15.2", GitCommit:"f6278300bebbb750328ac16ee6dd3aa7d3549568", GitTreeState:"clean", BuildDate:"2019-08-05T09:15:22Z", GoVersion:"go1.12.5", Compiler:"gc", Platform:"linux/amd64"}
```

```bash
[root@localhost ~]# kubectl cluster-info
Kubernetes master is running at https://192.168.221.129:8443
KubeDNS is running at https://192.168.221.129:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

```bash
[root@localhost ~]# kubectl get namespace
NAME              STATUS   AGE
default           Active   51m
kube-node-lease   Active   51m
kube-public       Active   51m
kube-system       Active   51m
```

```bash
[root@localhost ~]# kubectl get pods --namespace=kube-system
NAME                               READY   STATUS             RESTARTS   AGE
coredns-6967fb4995-vg7jt           0/1     CrashLoopBackOff   15         53m
coredns-6967fb4995-wvxs4           0/1     CrashLoopBackOff   15         53m
etcd-minikube                      1/1     Running            0          53m
kube-addon-manager-minikube        1/1     Running            0          53m
kube-apiserver-minikube            1/1     Running            0          53m
kube-controller-manager-minikube   1/1     Running            0          53m
kube-proxy-p54kz                   1/1     Running            0          53m
kube-scheduler-minikube            1/1     Running            0          53m
storage-provisioner                1/1     Running            0          53m
```





另外有一篇别人的安装minikube文章https://yq.aliyun.com/articles/221687