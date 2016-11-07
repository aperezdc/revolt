#! /bin/bash
#
# install.sh
# Copyright (C) 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.
#

declare -r APP_ID='org.perezdecastro.Revolt'

source "$(dirname "$0")/install-functions.sh"
install-setup "$0" "$@"

install-bin revolt
install-desktop-file "${APP_ID}.desktop"
install-glib-gschema "${APP_ID}.gschema.xml"
install-prefixed share/revolt "${APP_ID}.gresource" -m644

for size in 16 32 48 64 128 256 ; do
	install-icon "${APP_ID}" ${size} apps assets/icon-${size}.png
done
install-icon "${APP_ID}" scalable apps assets/icon.svg
install-icon "${APP_ID}" symbolic apps assets/icon-symbolic.svg

install-finish
