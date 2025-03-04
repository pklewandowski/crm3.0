# REPORT WIKI

## Report parameters mapping

### Common parameters:

- creation_date: default datetime.datetime.now()
- doc_creation_date: date of document created. Document.creation_date
- user: logged user, who crearted the report: request.user

### Mapping table parameters

codes in the array are ids of given attribuite

```json
{
  "someTable": [
    1111,
    2222,
    3333,
    4444
  ]
}
```

## Jinja2

Do not forget to install jinja2 in common venv

```bash
pip install jinja2
```

It may be needed to install also openpyxl

```bash
pip install openpyxl
```

## wkhtmltopdf on Linux
you have to install <span style="color: red;"><strong>!!! WITH patched QT !!!</strong></span>, otherwise don't render headers / footers. Example here:
```shell
sudo apt-get install xfonts-75dpi
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt --fix-broken install
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb
```
after insall it has to be like that:
```shell
$ wkhtmltopdf -V
wkhtmltopdf 0.12.6.1 (with patched qt)

```
you can also install: 
```shell
sudo apt-get install xvfb 
sudo pip install pyvirtualdisplay
```
## wkhtmltopdf [-6 error]: (patchedQt issue): can't read --header-html, --footer-html
### This instruction will help if you have error code -6 of wkhtmltopdf when you try to print.

- It works for Odoo 10 on Ubuntu Linux 16.04.3

```shell
# Uncomment the next line if you have installed wkhtmltopdf
# sudo apt remove wkhtmltopdf
cd ~
# Select an appropriate link for your system (32 or 64 bit) from the page https://wkhtmltopdf.org/downloads.html and past to the next line
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
tar xvf wkhtmltox*.tar.xz
sudo mv wkhtmltox/bin/wkhtmlto* /usr/bin
sudo apt-get install -y openssl build-essential libssl-dev libxrender-dev git-core libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig
```
OR
```shell
cd mytmpfolder
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo tar xvf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
sudo mv wkhtmltox/bin/wkhtmlto* /usr/bin/
#create simple html test file
echo "<html><body>test</body></html>" >> test.html
#perform conversion
sudo wkhtmltopdf  --disable-smart-shrinking  --lowquality --enable-external-links --enable-internal-links test.html test.pdf
```
then, in order to use pdfkit you need to change report generation code according to used OS:



```python
import pdfkit, os, crm_settings
from pyvirtualdisplay import Display

txt = "sometext"
path = 'someospath'

header_path = '/path/to/temporary/header/html/file.html'
footer_path = '/path/to/temporaryfooter/html/file.html'

config = pdfkit.configuration(wkhtmltopdf=crm_settings.WKHTMLTOPDF_PATH)
options = {
    "enable-local-file-access": None,
    'encoding': "UTF-8",
    "--header-html": header_path, 
    "--footer-html": footer_path, 
    # "margin-top": '20mm',
    # "margin-bottom": '15mm',
    "margin-left": '5mm',
    "margin-right": '5mm',
    # "--footer-center": "[page] / [topage]" to display pages but not not flexible if u have custom --footer-html
}
if os.name == 'nt':
    pdfkit.from_string(
        input=txt,
        output_path=path,
        configuration=config,
        options=options
    )
else:
    # needed for linux error wkhtmltopdf cannot connect to x-display
    with Display():
        pdfkit.from_string(
            input=txt,
            output_path=path,
            configuration=config,
            options=options
        )
```

## 2022-02-01 wkhtmltopdf update
There's no need to do above. You have only to:
```shell
sudo apt-get install xvfb
sudo pip install pyvirtualdisplay # on venv, Don't know if necessary
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.xenial_amd64.deb
sudo apt install ./wkhtmltox_0.12.6-1.xenial_amd64.deb
```
And it works fine :)\
<span style="color:red"><strong>CAUTION !!!</strong></span>\
home dir of wkhtmltopdf changed to /usr/local/

#UPDATE
Install 2022-03. latest release:
```shell
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb
sudo apt install ./wkhtmltox_0.12.6-1.focal_amd64.deb
```

