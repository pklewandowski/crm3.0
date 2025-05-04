# CRM INSTALATION GUIDE

## Installing PostgreSQL DB
## Installing python
## installing and configuring Nginx
## Installing and configuring Supervisor
## VENV
### Gunicorn execution file
## pip requirements installation
## Copying app files

## Installing Wkhtmltopdf (with patched QT)
```shell
sudo apt-get update 
sudo apt-get install -y wget xfonts-75dpi
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
# verifying installation
wkhtmltopdf --version

sudo apt-get install xvfb
```
