## Fix problem after package upgrade - apt upgrade
```shell
$ sudo apt install virtualbox 
$ sudo apt install --reinstall virtualbox-dkms && sudo apt install libelf-dev
```

## Allow to create symlinks
```VBoxManage.exe setextradata VM_NAME VBoxInternal2/SharedFoldersEnableSymlinksCreate/SHARED_NAME 1```

## Docker on Virtualbox and permissions for shared folder(s)
When creating docker for ie posgres and sudoing postgres su - postgres, it can't see the vbox shared folder 
content exposed by docker. to enable it:
```shell
# get id of the vboxsf group
getent group vboxsf

# add group in docker image
docker exec -it image_name bash
groupadd -g <gid> vboxsf
usermod -aG vboxsf postgres
```