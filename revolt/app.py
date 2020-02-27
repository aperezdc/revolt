#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016-2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

from os import environ
from gi.repository import Gtk, Gio, Gdk
from .statusicon import StatusIcon
from .window import MainWindow
from . import accelerators

DEFAULT_APP_ID = "org.perezdecastro.Revolt"
APP_ID = environ.get("REVOLT_OVERRIDE_APPLICATION_ID", DEFAULT_APP_ID).strip()

APP_COMMENTS = u"Desktop application for Riot.im"
APP_WEBSITE = u"https://github.com/aperezdc/revolt"
APP_AUTHORS = (u"Adrián Pérez de Castro <aperez@igalia.com>",
               u"Jacobo Aragunde Pérez <jaragunde@igalia.com>",
               u"Carlos López Pérez <clopez@igalia.com>")


def _find_resources_path(program_path):
    from os import path as P
    devel = environ.get("__REVOLT_DEVELOPMENT")
    if devel and devel.strip():
        # Use the directory where the executable is located, most likely
        # a checkout of the Git repository.
        path = P.dirname(P.dirname(program_path))
    else:
        # Use an installed location: binary is in <prefix>/bin/revolt,
        # and resources in <prefix>/share/revolt/*
        path = P.join(P.dirname(P.dirname(program_path)), "share", "revolt")
    return P.abspath(P.join(path, DEFAULT_APP_ID + ".gresource"))


class RevoltApp(Gtk.Application):
    def __init__(self, program_path):
        Gio.Resource.load(_find_resources_path(program_path))._register()
        Gtk.Application.__init__(self, application_id=APP_ID,
                                 resource_base_path="/" + DEFAULT_APP_ID.replace(".", "/"),
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.settings = Gio.Settings(schema_id=DEFAULT_APP_ID,
                                     path="/" + APP_ID.replace(".", "/") + "/")
        self.riot_url = self.settings.get_string("riot-url")
        self.window = None
        self._last_window_geometry = None
        self.statusicon = None
        self.connect("shutdown", self.__on_shutdown)
        self.connect("activate", self.__on_activate)
        self.connect("startup", self.__on_startup)

    def __action(self, name, callback):
        action = Gio.SimpleAction.new(name)
        action.connect("activate", callback)
        self.add_action(action)

    def __on_startup(self, app):
        gtk_settings = Gtk.Settings.get_default()
        gtk_settings.set_property("gtk-dialogs-use-header",
                                  self.settings.get_boolean("use-header-bar"))
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(self.get_resource_base_path() + "/gtk/custom.css")
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.statusicon = StatusIcon(self)
        self.__action("quit", lambda *arg: self.quit())
        self.__action("about", self.__on_app_about)
        self.__action("preferences", self.on_app_preferences)
        self.__action("riot-settings", self.on_riot_settings)

    def __on_shutdown(self, app):
        if self.window is not None:
            self.window.finish()

    def __on_activate(self, app):
        if self.window is None:
            saved_state_path = self.settings.get_property("path")
            saved_state_path += "saved-state/main-window/"
            saved_state = Gio.Settings(schema_id=DEFAULT_APP_ID + ".WindowState",
                                       path=saved_state_path)
            self.window = MainWindow(self, saved_state).load_riot()
        self.show()

    def __on_app_about(self, action, param):
        dialog = Gtk.AboutDialog(transient_for=self.window,
                                 program_name=u"Revolt",
                                 authors=APP_AUTHORS,
                                 logo_icon_name="revolt-about",
                                 license_type=Gtk.License.GPL_3_0,
                                 comments=APP_COMMENTS,
                                 website=APP_WEBSITE)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    def _build(self, resource, *names):
        builder = Gtk.Builder.new_from_resource(self.get_resource_base_path() + "/" + resource)
        return (builder.get_object(name) for name in names)

    def on_app_preferences(self, action, param):
        window, url_entry, zoom_factor, zoom_factor_reset, devtools_toggle = \
                self._build("gtk/preferences.ui",
                            "settings-window",
                            "riot-url-entry",
                            "zoom-factor",
                            "zoom-factor-reset",
                            "dev-tools-toggle")
        self.settings.bind("zoom-factor", zoom_factor, "value",
                           Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("enable-developer-tools", devtools_toggle, "active",
                           Gio.SettingsBindFlags.DEFAULT)
        zoom_factor_reset.connect("clicked", lambda button:
                                  self.settings.set_double("zoom-factor", 1.0))
        url_entry.set_text(self.riot_url)

        def on_hide(window):
            new_url = url_entry.get_text()
            if new_url != self.riot_url:
                self.settings.set_string("riot-url", new_url)
                self.riot_url = new_url
                self.window.load_riot()
        window.connect("hide", on_hide)
        window.add_accel_group(accelerators.window_close_on_escape)
        window.set_transient_for(self.window)
        window.present()

    def on_riot_settings(self, action, param):
        self.show()
        self.window.load_settings_page()

    def __save_window_geometry(self):
        window_size = self.window.get_size()
        window_position = self.window.get_position()
        self._last_window_geometry = {"width": window_size.width,
                                      "height": window_size.height,
                                      "root_x": window_position.root_x,
                                      "root_y": window_position.root_y}

    def __restore_window_geometry(self):
        if not self._last_window_geometry:
            return
        self.window.resize(self._last_window_geometry["width"],
                           self._last_window_geometry["height"])
        self.window.move(self._last_window_geometry["root_x"],
                         self._last_window_geometry["root_y"])
        # invalidate _last_window_geometry after restoring to ensure to
        # not restore again if the users clicks on the status icon when
        # the window is not hidden (like when minimized, or not focused)
        # self.hide() will take care of setting a new saved geometry.
        self._last_window_geometry = None

    def show(self):
        self.__restore_window_geometry()
        self.window.show()
        self.window.present()

    def hide(self):
        self.__save_window_geometry()
        self.window.hide()

    def is_visible_and_focused(self):
        return self.window.props.visible and self.window.props.has_toplevel_focus
