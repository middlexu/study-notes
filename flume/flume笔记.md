## netcat-mem-logger

```
# Name the components on this agent
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# Describe/configure the source
a1.sources.r1.type = netcat
a1.sources.r1.bind = localhost
a1.sources.r1.port = 44444

# Describe the sink
a1.sinks.k1.type = logger

# Use a channel which buffers events in memory
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100

# Bind the source and sink to the channel
a1.sources.r1.channels = c1
a1.sinks.k1.channel = c1    # channel没加s，说明不能多个channel发送给一个sink
```

```
启动flume
bin/flume-ng agent -c conf/ -n a1 -f job/netcat-mem-logger.conf -Dflume.root.logger=INFO,console
```




## taildir-mem-hadoop
监控文件TAILDIR,能够实现断点续传

```
a3.sources = r3 
a3.sinks = k3 
a3.channels = c3 
 
# Describe/configure the source 
a3.sources.r3.type = TAILDIR 
a3.sources.r3.positionFile = /opt/module/flume/tail_dir.json a3.sources.r3.filegroups = f1 
a3.sources.r3.filegroups.f1 = /opt/module/flume/files/file.*  

# Describe the sink 
a3.sinks.k3.type = hdfs 
a3.sinks.k3.hdfs.path = hdfs://hadoop102:9000/flume/upload/%Y%m%d/%H 
#上传文件的前缀 
a3.sinks.k3.hdfs.filePrefix = upload- 
#是否按照时间滚动文件夹 
a3.sinks.k3.hdfs.round = true 
#多少时间单位创建一个新的文件夹 
a3.sinks.k3.hdfs.roundValue = 1 
#重新定义时间单位 
a3.sinks.k3.hdfs.roundUnit = hour 
#是否使用本地时间戳 
a3.sinks.k3.hdfs.useLocalTimeStamp = true 
#积攒多少个Event才flush到HDFS一次 
a3.sinks.k3.hdfs.batchSize = 100 
#设置文件类型，可支持压缩 
a3.sinks.k3.hdfs.fileType = DataStream 
#多久生成一个新的文件 
a3.sinks.k3.hdfs.rollInterval = 60 
#设置每个文件的滚动大小大概是128M （要比128Mblock小一点）
a3.sinks.k3.hdfs.rollSize = 134217700 
#文件的滚动与Event数量无关 
a3.sinks.k3.hdfs.rollCount = 0 
 
# Use a channel which buffers events in memory a3.channels.c3.type = memory a3.channels.c3.capacity = 1000 
a3.channels.c3.transactionCapacity = 100 
 
# Bind the source and sink to the channel a3.sources.r3.channels = c3 a3.sinks.k3.channel = c3
```

 Taildir Source维护了一个json格式的position File，其会定期的往position File中更新每个文件读取到的最新的位置，因此能够实现断点续传。

Position File的格式如下： 
{"inode":2496272,"pos":12,"file":"/opt/module/flume/files/file1.t xt"} 
{"inode":2496275,"pos":12,"file":"/opt/module/flume/files/file2.t xt"} 



## 精髓：

+ channel向sink传递数据的时候，没有Replicating(复制)
  - source -> channel 
    Replicating（复制）
    Multiplexing（多路复用）
  - channel -> sink
    DefaultSinkProcessor (一个channel，一个sink)
    LoadBalancingSinkProcessor (一个channel，多个sink，负载均衡，可配置权重)
    FailoverSinkProcessor  (一个channel，多个sink，向权重大的sink发数据，权重大的挂了，才会向权重低的发)
+ flume与flume之间数据传递用avro，并且是接受端开启的服务器
+ 还可以自定义source和sink
+ source
  - spooldir监控文件夹，监视新增文件。上传完成的文件会以.COMPLETED 结尾。也就是说，这个文件夹里的文件不能修改
  - taildir监控目录下的多个追加文件，能实现断点续传。生产环境用的多。