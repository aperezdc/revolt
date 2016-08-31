Vector GNOME
============

Installation
------------

Install the files to their locations:

```sh
sudo ./install.sh --prefix=/usr --log-file=install.log
```

(Specifying a log file is optional, but if you plan on [upgrading](#upgrading)
later on using the `install.sh` script, it is recommended to use it.)

Install the dependencies:

```sh
sudo apt-get install python-gobject libwebkit2gtk-4.0
```

Now you should be able to launch Vector from the GNOME Shell.

### Upgrading

The `install.sh` script can be used to upgrade an existing installation as
well. The recommended way is to save a log of installed files, so the upgrade
process can remove stray files from the old version. In general, the preferred
way of invoking the installation script is as follows:

```sh
sudo ./install.sh --upgrade --prefix=/usr --log-file=/etc/vector-gnome.files
```

This way a log of the installed files is recorded the first time that the
installation is done, and further upgrades will use it to remove stray files
from old versions. Also, the log file will be updated with every upgrade.

### Flatpak

A basic, still not working flatpak can be created with the following commands:

```
flatpak build-init builddir com.igalia.VectorGnome org.gnome.Sdk org.gnome.Platform 3.20
flatpak build builddir ./install.sh --prefix=/app
flatpak build-finish .builddir --socket=x11 --share=network --command=vector
flatpak build-export repodir builddir
```
