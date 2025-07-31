FROM redis:latest
RUN apt update
RUN apt install -y vim
RUN mkdir /etc/redis
RUN echo "cluster-enabled yes\n\
cluster-config-file nodes.conf\n\
cluster-node-timeout 5000\n\
appendonly yes\n\
bind 0.0.0.0" > /etc/redis/redis.conf
# RUN /bin/bash
CMD ["redis-server", "/etc/redis/redis.conf"]