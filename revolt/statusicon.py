#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

from gi.repository import Gtk, GLib
import os


class SysTrayStatusIcon(object):
    ICON_STATUS_NAMES = ("connected", "disconnected", "flip", "flop")

    def __init__(self, app, initial_status):
        self._tooltip_text_no_notifications = "Revolt: 0 notifications"
        self.__app = app
        self._size = 16
        self._flipflop = True
        self._blinkmilliseconds = 500
        self._icon = self.__create_icon()
        self._contextmenu = \
            Gtk.Menu.new_from_model(self.__app.get_menu_by_id("app-menu"))
        self._contextmenu.insert_action_group("app", self.__app)
        self._icondata = {}
        self.__load_icons(self._size)
        self.set_status(initial_status)
        self.clear_notifications()

    def __add_notification_tooltip_text(self, text):
        if self._tooltip_text == self._tooltip_text_no_notifications:
            self._tooltip_text = ""
        self._tooltip_text += text
        self._tooltip_text += "\n"

    def __clear_notification_tooltip_text(self):
        self._tooltip_text = self._tooltip_text_no_notifications

    def __create_icon(self):
        icon = Gtk.StatusIcon()
        icon.set_visible(True)
        icon.set_property('has-tooltip', True)
        icon.set_property('title', 'Revolt')
        icon.connect('activate', self.__on_left_click)
        icon.connect('popup-menu', self.__on_right_click)
        icon.connect('query-tooltip', self.__on_query_tooltip)
        icon.connect('size-changed', self.__on_icon_size_change)
        return icon

    def __load_icons(self, size):
        self._size = size
        theme = Gtk.IconTheme.get_default()
        for status in self.ICON_STATUS_NAMES:
            self._icondata[status] = theme.load_icon("revolt-status-" + status, int(size), 0)

    def __draw_icon(self, status=None):
        if status is None:
            status = self.status
        if status == "blinking":
            if self._flipflop:
                self._icon.set_from_pixbuf(self._icondata["flip"])
            else:
                self._icon.set_from_pixbuf(self._icondata["flop"])
        else:
            self._icon.set_from_pixbuf(self._icondata[status])
        return False

    def __on_left_click(self, widget):
        self.clear_notifications()
        self.__app.show()

    def __on_right_click(self, icon, button, time):
        self._contextmenu.show_all()
        self._contextmenu.popup(None, None, None, self._icon, button, time)

    def __on_query_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        self._icon.set_tooltip_text(self._tooltip_text)

    def __on_icon_size_change(self, statusicon, size):
        if size > 31:
            icon_size = '32'
        elif size > 23:
            icon_size = '24'
        else:
            icon_size = '16'
        # detect KDE session. see gajim bug #5476
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            icon_size = '32'
        # detect MATE session.
        if os.environ.get('MATE_DESKTOP_SESSION_ID'):
            icon_size = '16'
        self.__load_icons(icon_size)
        self.__draw_icon()

    def __blink(self):
        self._flipflop = not self._flipflop
        self.__draw_icon()
        return self.status == "blinking"

    def add_notification(self, text):
        self.__add_notification_tooltip_text(text)
        self.set_status("blinking")

    def clear_notifications(self):
        self.__clear_notification_tooltip_text()
        if self.status == "blinking":
            self.set_status("connected")

    def set_status(self, status):
        valid_status = ["disconnected", "connected", "blinking"]
        if status not in valid_status:
            raise ValueError("Status %s is not valid. Allowed values are: %s" % (status, valid_status))
        if status == "blinking":
            # We only want one blink callback active at a time.
            if self.status != "blinking":
                GLib.timeout_add(self._blinkmilliseconds, self.__blink)
        else:
            GLib.timeout_add(2 * self._blinkmilliseconds, self.__draw_icon, status)
        self.status = status
