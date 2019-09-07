#!/bin/bash

case $1 in
"start"){
	for i in hadoop1 hadoop2 hadoop3
	do
		echo "*********$i*********"
		ssh $i '/opt/module/kafka/bin/kafka-server-start.sh -daemon /opt/module/kafka/config/server.properties'
	done
};;

"stop"){
	for i in hadoop1 hadoop2 hadoop3
	do
		echo "*********$i*********"
		ssh $i '/opt/module/kafka/bin/kafka-server-stop.sh /opt/module/kafka/config/server.properties'
	done
};;
esac


# 使用方法
# 开启Kafka集群：   kafkaCluster.sh start
# 关闭Kafka集群：   kafkaCluster.sh stop