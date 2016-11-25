#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.

import gi
gi.require_versions(dict(WebKit2='4.0',
                         Gtk='3.0',
                         GLib='2.0'))


def main(program_path):
    # Honor CTRL+C http://stackoverflow.com/q/16410852
    import signal
    import sys
    from .app import RevoltApp
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(RevoltApp(program_path).run(sys.argv[1:]))
