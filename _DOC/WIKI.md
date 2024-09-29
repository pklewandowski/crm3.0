# General help / info wiki base

## JavaScript / Browser tips & tricks

### Hold on autohide popover (like calendar window) for debugging
```javascript
setTimeout(function(){debugger;}, 5000);
```
this fires debugger in 5 sec. Effect is like on below screen:
![img.png](img.png)

## Frontend IDE config

### Install Webpack, MiniCssExtractPlugin, sass, css-loader, Babel
```sh
npm i webpack webpack-cli
npm i --save-dev mini-css-extract-plugin
npm i sass sass-loader
npm i css-loader
npm i @babel/preset-env --save-dev
```
##scp
### transfer file with password to remote host
```shell
apt-get -install sshpass
sshpass -p 'someP@sv0rd' scp /path/to/file.ext root@46.41.141.79:/path/to/remote/directory
```
## ssh
### enlarge timeout to ie./ 1 hr
```shell
$ sudo vi /etc/ssh/sshd_config
# then change parameters
ClientAliveInterval  1200
ClientAliveCountMax 3
# Timeout value = ClientAliveInterval * ClientAliveCountMax
# The Timeout value will be 1200 seconds * 3 = 3600 seconds
$ sudo systemctl reload sshd
````
## openssl
`openssl` command for creating self-signed certificates

params:
  * `-nodes` disables key password requirement
  * `-subj '/CN=localhost'` disables questions
```sh
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -nodes -subj '/CN=localhost'
```
# PostgreSQL
## PostgreSQL JSON field update

Przykład: kluczowa jest funkcja to_jsonb
```sql
update document_type_attribute dd
set feature = jsonb_set(feature, '{calculable, calcFunc}',
    to_jsonb(regexp_replace(replace(feature -> 'calculable' ->> 'calcFunc', 'document.getElementById', 'Input.getByCode'), '\r|\n', ' ', 'g')), false)
where id_document_type = 26
  and dd.feature -> 'calculable' notnull;
```

## PostgreSQL disabling constrains during replication
```shell
# before
SET session_replication_role TO 'replica'

# after
SET session_replication_role TO 'origin'
````

## Get data from other database
list of column in FROM clause must be defined in t(....) alias
```sql
create extension dblink;
SELECT dblink_connect('nordfinance','host=localhost port=5432 dbname=nordfinance user=nordfinance password=nordfinance options=-csearch_path=crm');
SELECT * FROM dblink('nordfinance', 'select name from crm.document_type_attribute') as t(name text);
```

## Get table '_' in table name like char 
use backslash before _ (dash char)
```sql
SELECT concat ('truncate table crm.', table_name, ';')
FROM information_schema.tables
WHERE table_schema = 'crm'
and table_name like 'h\_%'
```

# LibreOffice
## Install
```sh
sudo add-apt-repository ppa:libreoffice/ppa
sudo apt update
sudo apt install libreoffice
```
## Convert to PDF via command line

`libreoffice --headless --convert-to pdf:calc_pdf_Export --outdir pdf/ template.xlsx`

 `--outdir` parameter is optional
 
 # Using Django from terminal
 ```shell
> # set env variable to tell Django the name of settings module
> export $DJANGO_SETTINGS_MODULE=crm_settings  # here type settings filename
>
> # activate apropriate virtual environment
> source venv/bin/activate 
>
> # run python
> python

Python 3.6.9 (default, Apr 18 2020, 01:56:04)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.

>>> import django
>>> django.setup()
```
From this point one can use the app ie:
```sh
>>> from apps.document.models import Document
>>> Document.objects.get(pk=999999999)delete()
```
# Django Add empty migration example
```sh
python manage.py makemigrations --name migration_name app_name --empty
```

# Django SQL query only year od a date
```sh
ModelTable.objects.filter(date_column__year=2020)
```

# Django running test cases
```shell
python .\manage.py test apps.notification.tests.NotificationParamBindingTestCase
````
# POSTGRESQL
 - show config file location command
 ```sh
psql -U postgres -c 'SHOW config_file'
```
## Reassign ownership from role_1 to role_2
```shell
REASSIGN OWNED BY old_role [, ...] TO new_role
```

# Take screenshot with Python
```sh
>pip install pyautogui
>C:\WINDOWS\system32>python
Python 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> import pyautogui
>>> ms = pyautogui.screenshot()
>>> ms.save('D:\__TEMP\scr.png')
```


#pdfkit

 - options
 pdfkit.from_file('preliminarySchedule.html', 'preliminarySchedule.pdf', {"enable-local-file-access": None})
 
 - enable-local-file-access - allow to upload local files


#Linux
## set timezone
```shell
sudo ln -sf /usr/share/zoneinfo/America/Monterrey /etc/localtime
sudo ln -sf /usr/share/zoneinfo/Poland /etc/localtime
etc...
```
# Backup
##rsync backup
```sh
rsync -avP --delete -e ssh /path/to/source/dir/ user@server_address:/path/tp/dest/dir/
```
a - combined parameter including -r (recursively)\
v - verbose - prints output to terminal (only when backup created manually)\
P - show progress bar\
e ssh - safe transfer over ssh

Trailing slash ad the and of the source specification is important to tell rsync to sync content of given directory. Without it the direcroty itself will be also created\
example for HOMECLOUD (prod) -> OVH backup server:
```shell
rsync -avP --delete -e ssh /webapps/ root@51.91.126.252:/webapps/
```

# GIT

## List of defined aliases
```shell
git config --get-regexp alias
```

## store credential persistence
```shell
git config --global credential.helper store
git pull
Username for 'https://github.com': pklewandowski@gmail.com
Password for 'https://pklewandowski@gmail.com@github.com': 
Already up to date.

```