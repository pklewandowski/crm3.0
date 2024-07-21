# INSTALLING ENVIRONMENT ON UBUNTU 18+
## Installing database
### Postgres
 - Installing server
```sh
sudo apt-get update
```
Add PostgreSQL Repository
To install from the official repository, you first need to add it to your system.
Import the GPG repository key with the commands:
```sh
sudo apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
```
Then, add the PostgreSQL repository by typing:
```sh
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
```
Update the Package List.
After adding the official PostgreSQL repository, make sure to update the package list. Doing this ensures you install the latest PostgreSQL package.
```sh
sudo apt-get update
```
Install PostgreSQL.
To install PostgreSQL and the PostgreSQL contrib package (which provides additional features), use the following command:
```sh
sudo apt-get install postgresql postgresql-contrib
```
 - creating db owner user
```shell
su - postgres
psql
> CREATE ROLE db_owner_name WITH password 'password' SUPERUSER;
\q
```
 - Editing pg_hba.conf file
### App owner user and group

### Nginx

### Gunicorn



