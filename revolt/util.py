#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPv3 license.

from gi.repository import Gdk
from gi.repository import Gtk
import os


if hasattr(Gtk, "show_uri_on_window"):
    def show_uri(parent, uri, timestamp=None):
        """
        Show a gtk.

        Args:
            parent: (todo): write your description
            uri: (str): write your description
            timestamp: (int): write your description
        """
        if timestamp is None:
            timestamp = Gdk.CURRENT_TIME
        Gtk.show_uri_on_window(parent, uri, timestamp)
else:
    def show_uri(parent, uri, timestamp=None):
        """
        Show the gtk.

        Args:
            parent: (todo): write your description
            uri: (str): write your description
            timestamp: (int): write your description
        """
        if timestamp is None:
            timestamp = Gdk.CURRENT_TIME
        Gtk.show_uri(None, uri, timestamp)


class CachedProperty(object):
    __slots__ = ("value", "get_value")

    INVALID = object()

    def __init__(self, f):
        """
        Initialize the field

        Args:
            self: (todo): write your description
            f: (int): write your description
        """
        self.value = self.INVALID
        self.get_value = f

    def __call__(self, obj):
        """
        Calls the call to call.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        if self.value is self.INVALID:
            self.value = self.get_value(obj)
        return self.value


def cachedproperty(f, doc=None):
    """
    A property decorator which a property.

    Args:
        f: (todo): write your description
        doc: (todo): write your description
    """
    return property(CachedProperty(f), doc=doc)


def desktop_is(desktopname):
    """
    Determine whether desktop desktop desktop desktop desktop.

    Args:
        desktopname: (str): write your description
    """
    desktopname = desktopname.lower()
    if desktopname == "kde" and os.environ.get("KDE_FULL_SESSION") == "true":
        return True
    if desktopname == "mate" and os.environ.get("MATE_DESKTOP_SESSION_ID"):
        return True
    for desktopvarname in ["XDG_SESSION_DESKTOP", "DESKTOP_SESSION", "XDG_CURRENT_DESKTOP",
                           "XDG_SESSION_DESKTOP", "XDG_MENU_PREFIX", "GDMSESSION", "XDG_DATA_DIRS"]:
        desktopvarvalue = os.environ.get(desktopvarname)
        if desktopvarvalue and desktopname in desktopvarvalue.lower():
            return True
    return False
