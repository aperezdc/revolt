#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016-2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

from gi.repository import GLib, Gtk, Gio, WebKit2, GObject
from .util import cachedproperty, show_uri, desktop_is
from . import accelerators
from . import statusicon


class MainWindow(Gtk.ApplicationWindow):
    network_busy = GObject.Property(type=bool, default=False)

    def __init__(self, application, saved_state):
        self.application = application
        self.saved_state = saved_state
        Gtk.ApplicationWindow.__init__(self,
                                       application=application,
                                       icon_name="revolt",
                                       role="main-window",
                                       default_width=saved_state.get_uint("width"),
                                       default_height=saved_state.get_uint("height"))
        if self.saved_state.get_boolean("maximized"):
            self.maximize()
        self.saved_state.bind("maximized", self, "is-maximized", Gio.SettingsBindFlags.SET)

        if application.settings.get_boolean("use-header-bar"):
            self.set_titlebar(self.__make_headerbar())

        if application.settings.get_boolean("hide-on-window-close"):
            self.connect("delete-event", self.__hide_on_destroy)

        self.set_title(u"Revolt")
        application.add_window(self)
        self._webview = WebKit2.WebView(user_content_manager=self._user_content_manager,
                                        web_context=self._web_context)
        self._webview.connect("decide-policy", self.__on_decide_policy)
        self._webview.connect("context-menu", self.__on_context_menu)
        application.settings.bind("zoom-factor", self._webview, "zoom-level",
                                  Gio.SettingsBindFlags.GET)
        if hasattr(self._webview, "set_maintains_back_forward_list"):
            self._webview.set_maintains_back_forward_list(False)
        websettings = self._webview.get_settings()
        application.settings.bind("enable-developer-tools", websettings,
                                  "enable-developer-extras",
                                  Gio.SettingsBindFlags.GET)
        application.settings.bind("enable-developer-tools", websettings,
                                  "enable-write-console-messages-to-stdout",
                                  Gio.SettingsBindFlags.GET)

        self.add_accel_group(accelerators.window_keys)

        websettings.set_allow_file_access_from_file_urls(True)
        websettings.set_allow_modal_dialogs(False)  # TODO
        websettings.set_enable_fullscreen(False)
        websettings.set_enable_java(False)
        websettings.set_enable_media_stream(True)
        websettings.set_enable_page_cache(False)  # Single-page app
        websettings.set_enable_plugins(False)
        websettings.set_enable_smooth_scrolling(True)
        websettings.set_enable_webaudio(True)
        websettings.set_javascript_can_access_clipboard(True)
        websettings.set_minimum_font_size(12)  # TODO: Make it a setting
        websettings.set_property("enable-mediasource", True)

        # This makes Revolt lighter, and makes things work for people using
        # binary drivers (i.e. NVidia) with Flatpak build. See issue #29.
        if hasattr(websettings, "set_hardware_acceleration_policy"):
            websettings.set_hardware_acceleration_policy(WebKit2.HardwareAccelerationPolicy.NEVER)

        self._webview.show_all()
        self.add(self._webview)
        self.__connect_widgets()
        self.__notification_ids = set()

    def do_configure_event(self, event):
        result = Gtk.ApplicationWindow.do_configure_event(self, event)
        width, height = self.get_size()
        self.saved_state.set_uint("width", width)
        self.saved_state.set_uint("height", height)
        return result

    def __make_headerbar(self):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.get_style_context().add_class("revolt-slim")
        spinner = Gtk.Spinner()
        header.pack_end(spinner)
        self.bind_property("network-busy", spinner, "active",
                           GObject.BindingFlags.DEFAULT)
        header.show_all()
        return header

    @cachedproperty
    def _website_data_manager(self):
        from os import path as P
        print("Creating WebsiteDataManager...")
        app_id = self.application.get_application_id()
        cache_dir = P.join(GLib.get_user_cache_dir(), "revolt", app_id)
        data_dir = P.join(GLib.get_user_data_dir(), "revolt", app_id)
        return WebKit2.WebsiteDataManager(base_cache_directory=cache_dir,
                                          base_data_directory=data_dir)

    @cachedproperty
    def _web_context(self):
        print("Creating WebContext...")
        ctx = WebKit2.WebContext(website_data_manager=self._website_data_manager)
        ctx.set_spell_checking_enabled(False)
        ctx.set_tls_errors_policy(WebKit2.TLSErrorsPolicy.FAIL)
        return ctx

    @cachedproperty
    def _user_content_manager(self):
        mgr = WebKit2.UserContentManager()
        script = WebKit2.UserScript("Notification.requestPermission();",
                                    WebKit2.UserContentInjectedFrames.TOP_FRAME,
                                    WebKit2.UserScriptInjectionTime.START,
                                    None, None)
        mgr.add_script(script)
        return mgr

    def __on_decide_policy(self, webview, decision, decision_type):
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            if decision.get_navigation_type() == WebKit2.NavigationType.LINK_CLICKED:
                uri = decision.get_request().get_uri()
                if not uri.startswith(self.application.riot_url):
                    show_uri(self, uri)
                    return True
        elif decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
            if decision.get_navigation_type() == WebKit2.NavigationType.LINK_CLICKED:
                show_uri(self, decision.get_request().get_uri())
                return True
        return False

    @cachedproperty
    def _context_menu_actions(self):
        action_list = []
        action = Gio.SimpleAction.new("preferences")
        action.connect("activate", self.application.on_app_preferences)
        action_list.append((action, "_Preferences"))
        action = Gio.SimpleAction.new("riot-settings")
        action.connect("activate", self.application.on_riot_settings)
        action_list.append((action, "_Riot Settings"))
        return tuple(action_list)

    def __on_context_menu(self, webview, menu, event, hit_test):
        # Tweak built-in entries.
        for action in (WebKit2.ContextMenuAction.GO_BACK,
                       WebKit2.ContextMenuAction.GO_FORWARD,
                       WebKit2.ContextMenuAction.STOP):
            for index in range(menu.get_n_items()):
                item = menu.get_item_at_position(index)
                if action == item.get_stock_action():
                    menu.remove(item)
                    break
        # Add a separator.
        menu.append(WebKit2.ContextMenuItem.new_separator())
        # Append application-specfic entries.
        for (action, label) in self._context_menu_actions:
            menu.append(WebKit2.ContextMenuItem.new_from_gaction(action, label))
        return False

    def __on_has_toplevel_focus_changed(self, window, has_focus):
        assert window == self
        if window.has_toplevel_focus():
            # Clear the window's urgency hint
            window.set_urgency_hint(False)
            # Dismiss notifications
            for notification_id in self.__notification_ids:
                self.application.withdraw_notification(notification_id)
            self.__notification_ids.clear()
            self.application.statusicon.clear_notifications()

    def __on_load_changed(self, webview, event):
        if event == WebKit2.LoadEvent.FINISHED:
            self.network_busy = False
            self.application.statusicon.set_status(statusicon.Status.CONNECTED)
        else:
            self.network_busy = True
            self.application.statusicon.set_status(statusicon.Status.DISCONNECTED)

    @cachedproperty
    def _notification_icon(self):
        icon_id = self.application.get_application_id() + "-symbolic"
        return Gio.ThemedIcon.new(icon_id)

    def __on_show_notification(self, webview, notification):
        # TODO: Handle notification clicked, and so
        if not self.has_toplevel_focus():
            self.set_urgency_hint(True)
            notif = Gio.Notification.new(notification.get_title())
            notif.set_body(notification.get_body())
            # TODO: Use the avatar of the contact, if available.
            notif.set_icon(self._notification_icon)
            if not desktop_is("xfce"):  # Workaround for XFCE bug #13586
                notif.set_priority(Gio.NotificationPriority.HIGH)
            # use title as notification id:
            # allows to reuse one notification for the same conversation
            notification_id = notification.get_title()
            self.__notification_ids.add(notification_id)
            self.application.send_notification(notification_id, notif)
            self.application.statusicon.add_notification("%s: %s" % (notification.get_title(),
                                                                     notification.get_body()))
        return True

    def __on_permission_request(self, webview, request):
        if isinstance(request, WebKit2.NotificationPermissionRequest):
            request.allow()
            return True

    def __connect_widgets(self):
        self.connect("notify::has-toplevel-focus", self.__on_has_toplevel_focus_changed)
        self._webview.connect("load-changed", self.__on_load_changed)
        self._webview.connect("show-notification", self.__on_show_notification)
        self._webview.connect("permission-request", self.__on_permission_request)

    def __hide_on_destroy(self, widget, event):
        self.application.hide()
        return True

    def reload_riot(self, bypass_cache=False):
        if bypass_cache:
            self._webview.reload_bypass_cache()
        else:
            self._webview.reload()

    def load_riot(self):
        self._webview.load_uri(self.application.riot_url)
        return self

    def load_settings_page(self):
        from urllib.parse import urlsplit, urlunsplit
        url = list(urlsplit(self._webview.get_uri()))
        url[-1] = "#settings"
        self._webview.load_uri(urlunsplit(url))

    def finish(self):
        self._webview.stop_loading()
        self.hide()
        self.destroy()
        del self._webview
        return self
