#DOCKER
## Iteractive mode (-it)
```shell
docker exec -it a76135c90bdf bash
```
lub
```shell
docker exec -it [nazwa_przyjazna_kontenera] bash
```
np:
```shell
docker exec -it docker_postgresql_db_1 bash
```

## Recreating container
```shell
docker-compose up --force-recreate --build -d
```

## Stopping container
<span style="color:red"><strong>CAUTION !!!</strong></span>\
**Never** use `docker-compose down` if you don't want your persistent data and container state to be lost.\
Use `docker-compose stop` instead. `docker-compose down` stops the container **AND REMOVES** it!

## Backup container
```bash
# Check the ID of container
sudo docker container ls

CONTAINER ID   IMAGE           COMMAND                  CREATED       STATUS         PORTS                                       NAMES
e283bbb69bfd   postgres:13.1   "docker-entrypoint.s…"   11 days ago   Up 3 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   crm_postgresql_db_131

# Create internal container backup
sudo docker commit -p e283bbb69bfd docker-container-backup

# Save it as a tar file
sudo docker save -o /path/to/docker-container-backup-2021-11-01.tar docker-container-backup

```

##Restoring container
```sh
sudo docker load -i /path/to/docker-container-backup-2021-11-01.tar
```


















