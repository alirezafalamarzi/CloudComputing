# docker network create redis-cluster
docker network connect bridge redis1
docker network connect bridge redis2
docker network connect bridge redis3
docker network connect bridge redis4
docker network connect bridge redis5
docker network connect bridge redis6


docker exec -it redis1 redis-cli --cluster create \
  redis1:6379 redis2:6379 redis3:6379 redis4:6379 redis5:6379 redis6:6379 \
  --cluster-replicas 1