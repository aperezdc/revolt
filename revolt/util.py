#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPv3 license.

from gi.repository import Gdk
from gi.repository import Gtk


if hasattr(Gtk, "show_uri_on_window"):
    def show_uri(parent, uri, timestamp=None):
        if timestamp is None:
            timestamp = Gdk.CURRENT_TIME
        Gtk.show_uri_on_window(parent, uri, timestamp)
else:
    def show_uri(parent, uri, timestamp=None):
        if timestamp is None:
            timestamp = Gdk.CURRENT_TIME
        Gtk.show_uri(None, uri, timestamp)


class CachedProperty(object):
    __slots__ = ("value", "get_value")

    INVALID = object()

    def __init__(self, f):
        self.value = self.INVALID
        self.get_value = f

    def __call__(self, obj):
        if self.value is self.INVALID:
            self.value = self.get_value(obj)
        return self.value


def cachedproperty(f, doc=None):
    return property(CachedProperty(f), doc=doc)
