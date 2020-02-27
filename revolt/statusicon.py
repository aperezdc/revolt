#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016-2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

from gi.repository import Gtk, GLib
from .util import cachedproperty, desktop_is
import enum


class Status(enum.Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    BLINKING = "blinking"


class StatusIconImpl(object):
    def __init__(self, delegate):
        self.delegate = delegate

    def __del__(self):
        self.delegate = None

    def set_tooltip(self, text):
        raise NotImplementedError

    def set_status(self, status):
        raise NotImplementedError


class StatusIconImplSNI(StatusIconImpl):
    ICON_PIXBUF_SIZE = 64  # This seems to be a reasonable size for all DEs.

    def __init__(self, delegate, context_menu, app, failure_callback):
        super().__init__(delegate)

        import gi
        gi.require_version("StatusNotifier", "1.0")
        from gi.repository import StatusNotifier

        if hasattr(StatusNotifier.Icon, "ATTENTION_ICON"):
            self.SNI_ATTENTION_ICON = StatusNotifier.Icon.ATTENTION_ICON
            self.SNI_ACTIVE_ICON = StatusNotifier.Icon.ICON
        else:
            self.SNI_ATTENTION_ICON = StatusNotifier.Icon.STATUS_NOTIFIER_ATTENTION_ICON
            self.SNI_ACTIVE_ICON = StatusNotifier.Icon.STATUS_NOTIFIER_ICON
        self.SNI_ATTENTION = StatusNotifier.Status.NEEDS_ATTENTION
        self.SNI_ACTIVE = StatusNotifier.Status.ACTIVE

        theme = Gtk.IconTheme.get_default()
        self._offline_icon_pixbuf = theme.load_icon("org.perezdecastro.Revolt",
                                                    self.ICON_PIXBUF_SIZE,
                                                    Gtk.IconLookupFlags.FORCE_SVG |
                                                    Gtk.IconLookupFlags.FORCE_SYMBOLIC)
        self._attention_icon_pixbuf = theme.load_icon("org.perezdecastro.Revolt-status-blink",
                                                      self.ICON_PIXBUF_SIZE,
                                                      Gtk.IconLookupFlags.FORCE_SVG |
                                                      Gtk.IconLookupFlags.FORCE_SYMBOLIC)
        self._online_icon_pixbuf = theme.load_icon("org.perezdecastro.Revolt-status-online",
                                                   self.ICON_PIXBUF_SIZE,
                                                   Gtk.IconLookupFlags.FORCE_SVG |
                                                   Gtk.IconLookupFlags.FORCE_SYMBOLIC)

        self._failure_callback = failure_callback
        self._sni = StatusNotifier.Item.new_from_pixbuf(app.get_application_id(),
                                                        StatusNotifier.Category.COMMUNICATIONS,
                                                        self._offline_icon_pixbuf)
        if not self._sni.set_context_menu(context_menu):
            # TODO: No DbusMenu support built into StatusIcon, we need to handle the
            #  "context-menu" signal ourselves. For now, fallback to use GtkStatusIcon
            raise RuntimeError("StatusNotifier does not support DbusMenu, falling back to GtkStatusIcon")

        self._sni.connect("registration-failed", self.__on_registration_failed)
        self._sni.connect("activate", self.__on_activate)
        self._sni.set_from_pixbuf(self.SNI_ATTENTION_ICON, self._attention_icon_pixbuf)
        self._sni.set_title("Revolt")
        self._sni.set_status(self.SNI_ACTIVE)
        self._sni.set_item_is_menu(False)
        self._sni.freeze_tooltip()
        self._sni.set_tooltip_title("Revolt")
        self._sni.thaw_tooltip()
        self._sni.register()

    def set_status(self, status):
        if status is Status.BLINKING:
            self._sni.set_status(self.SNI_ATTENTION)
        else:
            self._sni.set_status(self.SNI_ACTIVE)
            if status is Status.CONNECTED:
                self._sni.set_from_pixbuf(self.SNI_ACTIVE_ICON, self._online_icon_pixbuf)
            elif status is Status.DISCONNECTED:
                self._sni.set_from_pixbuf(self.SNI_ACTIVE_ICON, self._offline_icon_pixbuf)
            else:
                assert False, "Unrechable"

    def __on_registration_failed(self, sni, error):
        assert sni == self._sni
        print("StatusNotifier registration failed, falling back to GtkStatusIcon")
        self._failure_callback(self)

    def __on_activate(self, sni, x, y):
        assert sni == self._sni
        self.delegate.on_icon_activate(self)

    def set_tooltip(self, text):
        self._sni.freeze_tooltip()
        self._sni.set_tooltip_body("" if text is None else text)
        self._sni.thaw_tooltip()


class StatusIconImplGSI(StatusIconImpl):
    ICON_STATUS_NAMES = {
        Status.DISCONNECTED.value: "",
        Status.CONNECTED.value: "-status-online",
        "flip": "-status-blink",
        "flop": ""
    }

    def __init__(self, delegate, context_menu, app):
        super().__init__(delegate)
        self._status = Status.DISCONNECTED
        self._contextmenu = context_menu
        self._size = 16
        self._flipflop = True
        self._blinkmilliseconds = 500
        self._icondata = {}
        self.__load_icons(self._size, app)
        self._icon = Gtk.StatusIcon()
        self._icon.set_visible(True)
        self._icon.set_property("has-tooltip", True)
        self._icon.set_property("title", "Revolt")
        self._icon.connect("activate", self.__on_activate)
        self._icon.connect("popup-menu", self.__on_popup_menu)
        self._icon.connect("size-changed", self.__on_icon_size_change)

    def set_tooltip(self, text):
        if text is None:
            self._icon.set_tooltip_text("Revolt")
        else:
            self._icon.set_tooltip_markup("<b>Revolt</b>\n{!s}".format(text))

    def set_status(self, status):
        if status is Status.BLINKING:
            # We only want one blink callback active at a time.
            if self._status is not Status.BLINKING:
                GLib.timeout_add(self._blinkmilliseconds, self.__blink)
        else:
            GLib.timeout_add(2 * self._blinkmilliseconds, self.__draw_icon, status)
        self._status = status

    def __load_icons(self, size, app=None):
        if app is None:
            app = Gtk.Application.get_default()
        self._size = size
        theme = Gtk.IconTheme.get_default()
        for status, icon_suffix in self.ICON_STATUS_NAMES.items():
            icon_name = "org.perezdecastro.Revolt" + icon_suffix
            self._icondata[status] = theme.load_icon(icon_name, int(size),
                                                     Gtk.IconLookupFlags.FORCE_SVG |
                                                     Gtk.IconLookupFlags.FORCE_SYMBOLIC)

    def __draw_icon(self, status=None):
        if status is None:
            status = self._status
        if status is Status.BLINKING:
            if self._flipflop:
                self._icon.set_from_pixbuf(self._icondata["flip"])
            else:
                self._icon.set_from_pixbuf(self._icondata["flop"])
        else:
            self._icon.set_from_pixbuf(self._icondata[status.value])
        return False

    def __on_activate(self, icon):
        assert icon == self._icon
        self.delegate.on_icon_activate(self)

    def __on_popup_menu(self, icon, button, time):
        assert icon == self._icon
        self._contextmenu.show_all()
        self._contextmenu.popup(None, None, None, self._icon, button, time)

    def __on_icon_size_change(self, statusicon, size):
        if size > 31:
            icon_size = "32"
        elif size > 23:
            icon_size = "24"
        else:
            icon_size = "16"
        if desktop_is("kde"):  # KDE: see gajim bug #5476
            icon_size = "32"
        if desktop_is("mate"):
            icon_size = "16"
        self.__load_icons(icon_size)
        self.__draw_icon()

    def __blink(self):
        self._flipflop = not self._flipflop
        self.__draw_icon()
        return self._status is Status.BLINKING


class StatusIcon(object):
    def __init__(self, app, initial_status=Status.DISCONNECTED):
        self.status = Status(initial_status)
        self.__app = app
        self.__tooltip = None
        # Try using StatusNotifier first
        self._contextmenu.insert_action_group("app", app)
        try:
            self._impl = StatusIconImplSNI(self, self._contextmenu, app, self.__sni_failed)
        except Exception as e:
            print("StatusNotifier failed, using GtkStatusIcon instead -", str(e))
            self.__sni_failed(None)
        self.__configure_impl()

    def __sni_failed(self, sni_impl):
        # Use the (deprecated) GtkStatusIcon as fallback
        self._impl = StatusIconImplGSI(self, self._contextmenu, self.__app)
        self.__configure_impl()

    def __configure_impl(self):
        self._impl.set_tooltip(None)
        self.clear_notifications()

    @cachedproperty
    def _contextmenu(self):
        model = self.__app.get_menu_by_id("app-menu")
        if model is None:
            # If showing the application menu in the GNOME Shell top bar is
            # disabled, then GtkApplication won't load gtk/menus.ui
            # automatically, but we still need it for the context menu.
            (model,) = self.__app._build("gtk/menus.ui", "app-menu")
        return Gtk.Menu.new_from_model(model)

    def __add_notification_tooltip_text(self, text):
        if self.__tooltip is None:
            self.__tooltip = text
        else:
            self.__tooltip += "\n"
            self.__tooltip += text
        self._impl.set_tooltip(self.__tooltip)

    def __clear_notification_tooltip_text(self):
        self._impl.set_tooltip(None)
        self.__tooltip = None

    def set_status(self, status):
        status = Status(status)
        if status is not self.status:
            self.status = status
            self._impl.set_status(self.status)

    def add_notification(self, text):
        self.__add_notification_tooltip_text(text)
        self.set_status(Status.BLINKING)

    def clear_notifications(self):
        self.__clear_notification_tooltip_text()
        self.set_status(Status.CONNECTED)

    # Delegate methods.
    def on_icon_activate(self, icon_impl):
        self.clear_notifications()
        if self.__app.is_visible_and_focused():
            self.__app.hide()
        else:
            self.__app.show()
