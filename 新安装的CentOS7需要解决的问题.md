## 新安装的CentOS7需要解决的问题

### 新装的CentOS7连不了网络

```bash
vi /etc/sysconfig/network-scripts/ifcfg-ens33

TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static  #<-更改为static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens33
UUID=5ca7ca9b-676c-44f6-84f2-30b06b6198d4
DEVICE=ens33
ONBOOT=yes       #<-更改为yes,下面都是要更改的，要看VM的设置。编辑-->虚拟网络编辑器-->VMnet8,NAT设置，可以查看到网关
IPADDR=192.168.221.129
PREFIX=24
GATEWAY=192.168.221.2
DNS1=8.8.8.8
DNS2=114.114.114.114
NETMASK=255.255.255.0
```

```bash
service network restart #重启网络服务
```

现在可以ping通外网了

```bash
ping www.baidu.com
```



### 设置阿里源

备份原文件

```bash
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
```

下载阿里的CentOS-Base.repo

```bash
curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
```

清除YUM缓存  与 生成新的YUM缓存

```bash
yum clean all
yum makecache
```





### JAVA安装

安装传输工具

```bash
yum -y install lrzsz
```

把文件拖进窗口

创建安装目录

```bash
mkdir /usr/local/java/
```

解压至安装目录

```bash
tar -zxvf jdk-8u201-linux-x64.tar.gz -C /usr/local/java/
```

设置环境变量

```bash
vi /etc/profile

export JAVA_HOME=/usr/local/java/jdk1.8.0_201
export JRE_HOME=${JAVA_HOME}/jre
export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib
export PATH=${JAVA_HOME}/bin:$PATH
```

使环境变量生效

```bash
source /etc/profile
```

添加软链接

```bash
ln -s /usr/local/java/jdk1.8.0_171/bin/java /usr/bin/java
```

检查

```bash
java -version
```





