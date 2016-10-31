Revolt
======

Revolt is a small application which wraps [Riot](https://riot.im) to provide
better integration with desktop environments in general, and
[GNOME](http://www.gnome.org) in particular.


Installation
------------

The recommended installation method is to use [Flatpak](http://flatpak.org).
Starting with version `0.6.13` using a single command is enough (if you want to
intall in you user directory, add `--user` to the command):

```sh
flatpak install --from https://flatpak.perezdecastro.org/revolt
```

Once installed, updates will be installed automatically when using `flatpak update`.

You can also download [the .flatpakref
file](https://flatpak.perezdecastro.org/revolt.flatpakref) and double-click on
it to have GNOME Software install the application. GNOME Software will also
notify you of updates and give you the option to install them.

### Portal Helpers

**IMPORTANT**: Many distributions *do not* install the XDG helper programs for
the sandboxed applications, which are needed for some features to work. Please
install them using your distribution's package manager:

* Debian: [xdg-desktop-portal-gtk](https://packages.debian.org/search?keywords=xdg-desktop-portal-gtk).
* Arch Linux: [xdg-desktop-portal-gtk](https://aur.archlinux.org/packages/xdg-desktop-portal-gtk/) (AUR).

Some features, remarkably the desktop notifications, _will not work without the
portal helpers_.


Manual Installation
-------------------

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

Now you should be able to launch Revolt from the GNOME Shell.

### Upgrading

The `install.sh` script can be used to upgrade an existing installation as
well. The recommended way is to save a log of installed files, so the upgrade
process can remove stray files from the old version. In general, the preferred
way of invoking the installation script is as follows:

```sh
sudo ./install.sh --upgrade --prefix=/usr --log-file=/etc/revolt.files
```

This way a log of the installed files is recorded the first time that the
installation is done, and further upgrades will use it to remove stray files
from old versions. Also, the log file will be updated with every upgrade.

Flatpak
-------

A bundle can be created using the included [make-flatpak.sh](make-flatpak.sh)
script. The script arranges calling `flatpak-builder` to build and create a
repository into `.flatpak-repo`. You can create a bundle from the repository
using:

```sh
flatpak build-bundle .flatpak-repo/ Revolt.flatpak org.perezdecastro.Revolt
```

Once the bundle is created, you can install and run it with:

```sh
flatpak install --user --bundle Revolt.flatpak
flatpak run org.perezdecastro.Revolt
```

