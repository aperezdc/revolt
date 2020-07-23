#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

from gi.repository import Gtk, Gdk, GLib


def __window_close(accel_group, window, key, modifiers):
    assert isinstance(window, Gtk.Window)
    window.close()


window_close_on_escape = Gtk.AccelGroup()
window_close_on_escape.connect(Gdk.KEY_Escape, 0, 0, __window_close)


def __window_modify_zoom(accel_group, window, key, modifiers):
    if key == Gdk.KEY_0:
        window.application.settings.reset("zoom-factor")
    else:
        zoom = window.application.settings.get_double("zoom-factor")
        if key == Gdk.KEY_plus:
            zoom += 0.1
        elif key == Gdk.KEY_minus:
            zoom -= 0.1
        else:
            assert False, "Unreachable"
        schema = window.application.settings.get_property("settings-schema")
        value = GLib.Variant.new_double(zoom)
        if schema.get_key("zoom-factor").range_check(value):
            window.application.settings.set_value("zoom-factor", value)


def __window_webview_reload(accel_group, window, key, modifiers):
    window.reload_element(bypass_cache=True)


window_keys = Gtk.AccelGroup()
window_keys.connect(Gdk.KEY_r, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, 0,
                    __window_webview_reload)
for key in (Gdk.KEY_plus, Gdk.KEY_minus, Gdk.KEY_0):
    window_keys.connect(key, Gdk.ModifierType.CONTROL_MASK, 0, __window_modify_zoom)
