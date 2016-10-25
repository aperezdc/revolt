<s>Vector</s> Riot <s>GNOME</s>
===============================

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

Now you should be able to launch Riot from the GNOME Shell.

### Upgrading

The `install.sh` script can be used to upgrade an existing installation as
well. The recommended way is to save a log of installed files, so the upgrade
process can remove stray files from the old version. In general, the preferred
way of invoking the installation script is as follows:

```sh
sudo ./install.sh --upgrade --prefix=/usr --log-file=/etc/riot-gnome.files
```

This way a log of the installed files is recorded the first time that the
installation is done, and further upgrades will use it to remove stray files
from old versions. Also, the log file will be updated with every upgrade.

### Flatpak

A bundle can be created using the included [make-flatpak.sh](make-flatpak.sh)
script. The script arranges calling `flatpak-builder` to build and create a
repository into `.flatpak-repo`. You can create a bundle from the repository
using:

```sh
flatpak build-bundle .flatpak-repo/ vector-gnome.flatpak com.igalia.VectorGnome
```

Once the bundle is created, you can install and run it with:

```sh
flatpak install --user --from vector-gnome.flatpakref
flatpak run com.igalia.VectorGnome
```

