## Docker 运行时资源限制

Docker 基于 Linux 内核提供的 cgroups 功能，可以限制容器在运行时使用到的资源，比如内存、CPU、块 I/O、网络等。

### 内存限制

#### 概述

Docker 提供的内存限制功能有以下几点：

- 容器能使用的内存和交换分区大小。
- 容器的核心内存大小。
- 容器虚拟内存的交换行为。
- 容器内存的软性限制。
- 是否杀死占用过多内存的容器。
- 容器被杀死的优先级

一般情况下，达到内存限制的容器过段时间后就会被系统杀死。



#### 内存限制相关的参数

执行`docker run`命令时能使用的和内存限制相关的所有选项如下。

| 选项                   | 描述                                                         |
| ---------------------- | ------------------------------------------------------------ |
| `-m,--memory`          | 内存限制，格式是数字加单位，单位可以为 b,k,m,g。最小为 4M    |
| `--memory-swap`        | 内存+交换分区大小总限制。格式同上。必须必-m设置的大          |
| `--memory-reservation` | 内存的软性限制。格式同上。内存不会长时间的超过这个值         |
| `--oom-kill-disable`   | 是否阻止 OOM killer 杀死容器，默认没设置                     |
| `--oom-score-adj`      | 容器被 OOM killer 杀死的优先级，范围是[-1000, 1000]，默认为 0 |
| `--memory-swappiness`  | 用于设置容器的虚拟内存控制行为。值为 0~100 之间的整数        |
| `--kernel-memory`      | 核心内存限制。格式同上，最小为 4M                            |



#### 用户内存限制

用户内存限制就是对容器能使用的内存和交换分区的大小作出限制。使用时要遵循两条直观的规则：`-m，--memory`选项的参数最小为 4 M。`--memory-swap`不是交换分区，而是内存加交换分区的总大小，所以`--memory-swap`必须比`-m,--memory`大。在这两条规则下，一般有四种设置方式。（**一般不用交换分区，性能很低**）

> 你可能在进行内存限制的实验时发现docker run命令报错：WARNING: Your kernel does not support swap limit capabilities, memory limited without swap.
>
> 这是因为宿主机内核的相关功能没有打开。按照下面的设置就行。
>
> step 1：编辑/etc/default/grub文件，将GRUB_CMDLINE_LINUX一行改为GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"
>
> step 2：更新 GRUB，即执行$ sudo update-grub
>
> step 3: 重启系统。

1. **不设置**

如果不设置`-m,--memory`和`--memory-swap`，容器默认可以用完宿舍机的所有内存和 swap 分区。不过注意，如果容器占用宿主机的所有内存和 swap 分区超过一段时间后，会被宿主机系统杀死（如果没有设置`--00m-kill-disable=true`的话）。

2. **设置`-m,--memory`，不设置`--memory-swap`**

给`-m`或`--memory`设置一个不小于 4M 的值，假设为 a，不设置`--memory-swap`，或将`--memory-swap`设置为 0。这种情况下，容器能使用的内存大小为 a，能使用的交换分区大小也为 a。因为 Docker 默认容器交换分区的大小和内存相同。

如果在容器中运行一个一直不停申请内存的程序，你会观察到该程序最终能占用的内存大小为 2a。

比如`$ docker run -m 1G ubuntu:16.04`，该容器能使用的内存大小为 1G，能使用的 swap 分区大小也为 1G。容器内的进程能申请到的总内存大小为 2G。

3. **设置`-m,--memory=a`，`--memory-swap=b`，且b > a**

给`-m`设置一个参数 a，给`--memory-swap`设置一个参数 b。a 时容器能使用的内存大小，b是容器能使用的 内存大小 + swap 分区大小。所以 b 必须大于 a。b -a 即为容器能使用的 swap 分区大小。

比如`$ docker run -m 1G --memory-swap 3G ubuntu:16.04`，该容器能使用的内存大小为 1G，能使用的 swap 分区大小为 2G。容器内的进程能申请到的总内存大小为 3G。

4. **设置-m,--memory=a，--memory-swap=-1**

给`-m`参数设置一个正常值，而给`--memory-swap`设置成 -1。这种情况表示限制容器能使用的内存大小为 a，而不限制容器能使用的 swap 分区大小。

这时候，容器内进程能申请到的内存大小为 a + 宿主机的 swap 大小。



#### Memory reservation

这种 memory reservation 机制不知道怎么翻译比较形象。Memory reservation 是一种软性限制，用于节制容器内存使用。给`--memory-reservation`设置一个比`-m`小的值后，虽然容器最多可以使用-m使用的内存大小，但在宿主机内存资源紧张时，在系统的下次内存回收时，系统会回收容器的部分内存页，强迫容器的内存占用回到`--memory-reservation`设置的值大小。

没有设置时（默认情况下）`--memory-reservation`的值和-m的限定的值相同。将它设置为 0 或者设置的比`-m`的参数大 等同于没有设置。

**Memory reservation 是一种软性机制，它不保证任何时刻容器使用的内存不会超过`--memory-reservation`限定的值，它只是确保容器不会长时间占用超过--memory-reservation限制的内存大小。**

例如：

```sh
$ docker run -it -m 500M --memory-reservation 200M ubuntu:16.04 /bin/bash
```

如果容器使用了大于 200M 但小于 500M 内存时，下次系统的内存回收会尝试将容器的内存锁紧到 200M 以下。

例如：

```sh
$ docker run -it --memory-reservation 1G ubuntu:16.04 /bin/bash
```

容器可以使用尽可能多的内存。`--memory-reservation`确保容器不会长时间占用太多内存。



#### OOM killer

默认情况下，在出现 out-of-memory(OOM) 错误时，系统会杀死容器内的进程来获取更多空闲内存。这个杀死进程来节省内存的进程，我们姑且叫它 OOM killer。我们可以通过设置`--oom-kill-disable`选项来禁止 OOM killer 杀死容器内进程。但请确保只有在使用了`-m/--memory`选项时才使用`--oom-kill-disable`禁用 OOM killer。如果没有设置-m选项，却禁用了 OOM-killer，可能会造成出现 out-of-memory 错误时，系统通过杀死宿主机进程或获取更改内存。

下面的例子限制了容器的内存为 100M 并禁止了 OOM killer：

```shell
$ docker run -it -m 100M --oom-kill-disable ubuntu:16.04 /bin/bash
```


是正确的使用方法。

而下面这个容器没设置内存限制，却禁用了 OOM killer 是非常危险的：

```shell
$ docker run -it --oom-kill-disable ubuntu:16.04 /bin/bash
```


容器没用内存限制，可能或导致系统无内存可用，并尝试时杀死系统进程来获取更多可用内存。

一般一个容器只有一个进程，这个唯一进程被杀死，容器也就被杀死了。我们可以通过--oom-score-adj选项来设置在系统内存不够时，容器被杀死的优先级。负值更教不可能被杀死，而正值更有可能被杀死。



#### 核心内存

核心内存和用户内存不同的地方在于核心内存不能被交换出。不能交换出去的特性使得容器可以通过消耗太多内存来堵塞一些系统服务。核心内存包括：

- stack pages（栈页面）
- slab pages
- socket memory pressure
- tcp memory pressure

可以通过设置核心内存限制来约束这些内存。例如，每个进程都要消耗一些栈页面，通过限制核心内存，可以在核心内存使用过多时阻止新进程被创建。

核心内存和用户内存并不是独立的，必须在用户内存限制的上下文中限制核心内存。

假设用户内存的限制值为 U，核心内存的限制值为 K。有三种可能地限制核心内存的方式：

1. U != 0，不限制核心内存。这是默认的标准设置方式
2. K < U，核心内存是用户内存的子集。这种设置在部署时，每个 cgroup 的内存总量被过度使用。过度使用核心内存限制是绝不推荐的，因为系统还是会用完不能回收的内存。在这种情况下，你可以设置 K，这样 groups 的总数就不会超过总内存了。然后，根据系统服务的质量自有地设置 U。
3. K > U，因为核心内存的变化也会导致用户计数器的变化，容器核心内存和用户内存都会触发回收行为。这种配置可以让管理员以一种统一的视图看待内存。对想跟踪核心内存使用情况的用户也是有用的。

例如：

```shell
$ docker run -it -m 500M --kernel-memory 50M ubuntu:16.04 /bin/bash
```

容器中的进程最多能使用 500M 内存，在这 500M 中，最多只有 50M 核心内存。

```shell
$ docker run -it --kernel-memory 50M ubuntu:16.04 /bin/bash
```


没用设置用户内存限制，所以容器中的进程可以使用尽可能多的内存，但是最多能使用 50M 核心内存。



#### Swappiness

默认情况下，容器的内核可以交换出一定比例的匿名页。`--memory-swappiness`就是用来设置这个比例的。`--memory-swappiness`可以设置为从 0 到 100。0 表示关闭匿名页面交换。100 表示所有的匿名页都可以交换。默认情况下，如果不适用`--memory-swappiness`，则该值从父进程继承而来。

例如：

```shell
$ docker run -it --memory-swappiness=0 ubuntu:16.04 /bin/bash
```

将`--memory-swappiness`设置为 0 可以保持容器的工作集，避免交换代理的性能损失。





### CPU 限制

#### 概述

Docker 的资源限制和隔离完全基于 Linux cgroups。对 CPU 资源的限制方式也和 cgroups 相同。Docker 提供的 CPU 资源限制选项可以在多核系统上限制容器能利用哪些 vCPU。而对容器最多能使用的 CPU 时间有两种限制方式：一是有多个 CPU 密集型的容器竞争 CPU 时，设置各个容器能使用的 CPU 时间相对比例。二是以绝对的方式设置容器在每个调度周期内最多能使用的 CPU 时间。

#### CPU 限制相关参数

docker run命令和 CPU 限制相关的所有选项如下：

| **选项**              | **描述**                                                |
| --------------------- | ------------------------------------------------------- |
| `--cpuset-cpus=""`    | 允许使用的 CPU 集，值可以为 0-3,0,1                     |
| `-c`,`--cpu-shares=0` | CPU 共享权值（相对权重）                                |
| `cpu-period=0`        | 限制 CPU CFS 的周期，范围从 100ms~1s，即[1000, 1000000] |
| `--cpu-quota=0`       | 限制 CPU CFS 配额，必须不小于1ms，即 >= 1000            |
| `--cpuset-mems=""`    | 允许在上执行的内存节点（MEMs），只对 NUMA 系统有效      |


其中`--cpuset-cpus`用于设置容器可以使用的 vCPU 核。`-c`,`--cpu-shares`用于设置多个容器竞争 CPU 时，各个容器相对能分配到的 CPU 时间比例。`--cpu-period`和`--cpu-quata`用于绝对设置容器能使用 CPU 时间。

`--cpuset-mems`暂用不上，这里不谈。



#### CPU 集

我们可以设置容器可以在哪些 CPU 核上运行。

例如：

```shell
$ docker run -it --cpuset-cpus="1,3" ubuntu:14.04 /bin/bash
```

表示容器中的进程可以在 cpu 1 和 cpu 3 上执行。

```shell
$ docker run -it --cpuset-cpus="0-2" ubuntu:14.04 /bin/bash
```

表示容器中的进程可以在 cpu 0、cpu 1 及 cpu 2 上执行。

在 NUMA 系统上，我们可以设置容器可以使用的内存节点。

例如：

```shell
$ docker run -it --cpuset-mems="1,3" ubuntu:14.04 /bin/bash
```

表示容器中的进程只能使用内存节点 1 和 3 上的内存。

```shell
$ docker run -it --cpuset-mems="0-2" ubuntu:14.04 /bin/bash
```

表示容器中的进程只能使用内存节点 0、1、2 上的内存。



#### CPU 资源的相对限制

默认情况下，所有的容器得到同等比例的 CPU 周期。在有多个容器竞争 CPU 时我们可以设置每个容器能使用的 CPU 时间比例。这个比例叫作共享权值，通过`-c`或`--cpu-shares`设置。Docker 默认每个容器的权值为 1024。不设置或将其设置为 0，都将使用这个默认值。系统会根据每个容器的共享权值和所有容器共享权值和比例来给容器分配 CPU 时间。

假设有三个正在运行的容器，这三个容器中的任务都是 CPU 密集型的。第一个容器的 cpu 共享权值是 1024，其它两个容器的 cpu 共享权值是 512。第一个容器将得到 50% 的 CPU 时间，而其它两个容器就只能各得到 25% 的 CPU 时间了。如果再添加第四个 cpu 共享值为 1024 的容器，每个容器得到的 CPU 时间将重新计算。第一个容器的CPU 时间变为 33%，其它容器分得的 CPU 时间分别为 16.5%、16.5%、33%。

必须注意的是，这个比例只有在 CPU 密集型的任务执行时才有用。在四核的系统上，假设有四个单进程的容器，它们都能各自使用一个核的 100% CPU 时间，不管它们的 cpu 共享权值是多少。

在多核系统上，CPU 时间权值是在所有 CPU 核上计算的。即使某个容器的 CPU 时间限制少于 100%，它也能使用各个 CPU 核的 100% 时间。

例如，假设有一个不止三核的系统。用-c=512的选项启动容器{C0}，并且该容器只有一个进程，用-c=1024的启动选项为启动容器{C1}，并且该容器有两个进程。CPU 权值的分布可能是这样的：

```
PID    container    CPU CPU share
100    {C0}     0   100% of CPU0
101    {C1}     1   100% of CPU1
102    {C1}     2   100% of CPU2
```



#### CPU 资源的绝对限制

Linux 通过 CFS（Completely Fair Scheduler，完全公平调度器）来调度各个进程对 CPU 的使用。CFS 默认的调度周期是 100ms。

> 关于 CFS 的更多信息，参考CFS documentation on bandwidth limiting。

我们可以设置每个容器进程的调度周期，以及在这个周期内各个容器最多能使用多少 CPU 时间。使用--cpu-period即可设置调度周期，使用`--cpu-quota`即可设置在每个周期内容器能使用的 CPU 时间。两者一般配合使用。

例如：

```shell
$ docker run -it --cpu-period=50000 --cpu-quota=25000 ubuntu:16.04 /bin/bash
```

将 CFS 调度的周期设为 50000，将容器在每个周期内的 CPU 配额设置为 25000，表示该容器每 50ms 可以得到 50% 的 CPU 运行时间。

```shell
$ docker run -it --cpu-period=10000 --cpu-quota=20000 ubuntu:16.04 /bin/bash
```

将容器的 CPU 配额设置为 CFS 周期的两倍，CPU 使用时间怎么会比周期大呢？其实很好解释，给容器分配两个 vCPU 就可以了。该配置表示容器可以在每个周期内使用两个 vCPU 的 100% 时间。

CFS 周期的有效范围是 1ms~1s，对应的`--cpu-period`的数值范围是 1000~1000000。而容器的 CPU 配额必须不小于 1ms，即`--cpu-quota`的值必须 >= 1000。可以看出这两个选项的单位都是 us。



#### 正确的理解“绝对”

注意前面**我们用`--cpu-quota`设置容器在一个调度周期内能使用的 CPU 时间时实际上设置的是一个上限。并不是说容器一定会使用这么长的 CPU 时间。**比如，我们先启动一个容器，将其绑定到 cpu 1 上执行。给其--cpu-quota和--cpu-period都设置为 50000。

```shell
$ docker run --rm --name test01 --cpu-cpus 1 --cpu-quota=50000 --cpu-period=50000 deadloop:busybox-1.25.1-glibc
```

调度周期为 50000，容器在每个周期内最多能使用 50000 cpu 时间。

再用`docker stats test01`可以观察到该容器对 CPU 的使用率在100%左右。然后，我们再以同样的参数启动另一个容器。

```shell
$ docker run --rm --name test02 --cpu-cpus 1 --cpu-quota=50000 --cpu-period=50000 deadloop:busybox-1.25.1-glibc
```

再用`docker stats test01 test02`可以观察到这两个容器，每个容器对 cpu 的使用率在 50% 左右。说明容器并没有在每个周期内使用 50000 的 cpu 时间。

使用`docker stop test02`命令结束第二个容器，再加一个参数`-c 2048`启动它：

```shell
$ docker run --rm --name test02 --cpu-cpus 1 --cpu-quota=50000 --cpu-period=50000 -c 2048 deadloop:busybox-1.25.1-glibc
```

再用`docker stats test01`命令可以观察到第一个容器的 CPU 使用率在 33% 左右，第二个容器的 CPU 使用率在 66% 左右。因为第二个容器的共享值是 2048，第一个容器的默认共享值是 1024，所以第二个容器在每个周期内能使用的 CPU 时间是第一个容器的两倍。

原文：https://blog.csdn.net/candcplusplus/article/details/53728507 
