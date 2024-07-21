### Freze without version
```shell
pip freeze | sed s/=.*//
```