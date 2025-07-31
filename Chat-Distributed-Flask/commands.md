# To run docker cluster:

<!-- docker exec -it redis1 redis-cli --cluster create host.docker.internal:9001 host.docker.internal:9002 host.docker.internal:9003 host.docker.internal:9004 host.docker.internal:9005 host.docker.internal:9006 --cluster-replicas 1 -->


docker network create bridge
docker network connect bridge redis1
docker network connect bridge redis2
docker network connect bridge redis3
docker network connect bridge redis4
docker network connect bridge redis5
docker network connect bridge redis6


docker exec -it redis1 redis-cli --cluster create \
  redis1:6379 redis2:6379 redis3:6379 redis4:6379 redis5:6379 redis6:6379 \
  --cluster-replicas 1