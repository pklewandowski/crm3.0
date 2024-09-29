#!/bin/bash
# script works from app server handling prod crm applications
cd /webapps/opencash/prj/_deploy || exit
echo 'Backup apps'
echo '-------------------------------------------------------------'
read -sp "Enter password: " password
echo 'Sync remote backup...'
echo '--------------------------------------------------------------'
sshpass -p "$password" rsync -avP --delete -e ssh /webapps/ root@51.91.126.252:/webapps/