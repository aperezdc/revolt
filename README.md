![Logo](https://github.com/aperezdc/revolt/blob/master/assets/revolt-logo.png)

Revolt
======

Revolt is a small application which wraps [Riot](https://riot.im) to provide
better integration with desktop environments in general, and
[GNOME](http://www.gnome.org) in particular:

* Having Riot as a “standalone” application with its own window, launcher,
  icon, etc. instead of it living in a browser tab.
* Persistent notifications (for desktop environments supporting them, i.e.
  GNOME). Notifications are automatically prevented when the Revolt window is
  focused.
* Status icon for desktop environment which have a tray bar applet (XFCE,
  Budgie, likely many others).

![Status icon in Budgie](https://github.com/aperezdc/revolt/blob/master/assets/revolt-statusicon-screenshot.png)
![Application Window](https://github.com/aperezdc/revolt/blob/master/assets/revolt-screenshot.png)


Installation
------------

The recommended installation method is to use [Flatpak](http://flatpak.org).
Starting with version `0.6.13` using a single command is enough (if you want to
intall in you user directory, add `--user` to the command):

```sh
flatpak install --from https://flatpak.perezdecastro.org/revolt.flatpakref
```

If your Flatpak version is older than 0.6.13, use the following commands
instead:

```sh
wget https://flatpak.perezdecastro.org/revolt.flatpakref
flatpak install --from revolt.flatpakref
rm revolt.flatpakref
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
* Arch Linux: [xdg-desktop-portal-gtk](https://www.archlinux.org/packages/extra/x86_64/xdg-desktop-portal-gtk/).
* Fedora: [xdg-desktop-portal-gtk](https://admin.fedoraproject.org/pkgdb/package/rpms/xdg-desktop-portal-gtk/).

Some features, remarkably the desktop notifications, _will not work without the
portal helpers_.

### GNOME Runtime

Revolt uses the GNOME Flatpak runtime. Depending on the version of Flatpak
installed on your system, you may need to instal it manually. You can check
whether the runtime is missing by trying to run Revolt in a terminal:

```
% flatpak run org.perezdecastro.Revolt
error: runtime/org.gnome.Platform/x86_64/3.22 not installed
%
```

If you need to install the runtime manually, you can do so by issuing the
following command:

```
flatpak [--user] remote-add --from gnome https://sdk.gnome.org/gnome.flatpakrepo
```

If your Flatpak version is older than 0.6.13, use the following commands
instead:

```sh
wget https://sdk.gnome.org/keys/gnome-sdk.gpg
flatpak [--user] remote-add --gpg-import=gnome-sdk.gpg gnome https://sdk.gnome.org/repo/
flatpak [--user] install gnome org.gnome.Platform 3.22
```

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
sudo apt-get install python-gobject python3-gi libwebkit2gtk-4.0
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


Development
-----------

Using `make run` executes Revolt in “development” mode: the needed resources
are loaded from the source directory, instead of using the system-wide
directories.


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

