## Note
*Fork from [https://github.com/Icinga/icingadb.git](https://github.com/Icinga/docker-icingadb.git)*

*Dockerfile and Entrypoint have been adjusted to align with the NMAA Helm Chart*

*Change version parameter if building new version*

## Build new version

```bash
docker buildx build -f Dockerfile -t svtechnmaa/svtech_icingadb:v1.1.1 .
docker login -u svtechnmaa
docker push svtechnmaa/svtech_icingadb:v1.1.1 
```

