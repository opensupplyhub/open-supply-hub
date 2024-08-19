FROM amazonlinux:latest

WORKDIR /opt/
RUN yum install -y java-1.8.0 wget tar
RUN wget https://dlcdn.apache.org/kafka/3.8.0/kafka_2.13-3.8.0.tgz
RUN tar -xzf kafka_2.13-3.8.0.tgz
RUN ln /opt/kafka_2.13-3.8.0/bin/kafka-topics.sh /bin/kafka-topics
WORKDIR /opt/kafka_2.13-3.8.0/
COPY ssl.config kafka.sh list.txt .

RUN chmod +x kafka.sh