#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

from gi.repository import Gtk, Gdk


def __window_close(accel_group, window, key, modifiers):
    assert isinstance(window, Gtk.Window)
    window.close()

window_close_on_escape = Gtk.AccelGroup()
window_close_on_escape.connect(Gdk.KEY_Escape, 0, 0, __window_close)
