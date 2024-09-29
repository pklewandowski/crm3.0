1. Add newest libreoffice repo
2. Update apt
3. Install libreoffice writer (only writer is needed)

```shell
sudo add-apt-repository ppa:libreoffice/ppa
sudo apt update
sudo apt install libreoffice-writer
```

4. Convert to pdf

```shell
lowriter --convert-to pdf /path/to/docx/file /path/to/pdf/file
```

## Python example

```python
import subprocess

subprocess.run([
    'lowriter',
    '--convert-to',
    'pdf',
    '/mnt/ntfs/d/3WS/PROJEKTY/OPEN_CASH/_DOC/pisma_wychodzace/wdz.docx',
    '--outdir',  # optional
    '/tmp/'  # optional
])
```

