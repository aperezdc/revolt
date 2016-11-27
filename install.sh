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

install-bin bin/revolt
install-desktop-file "${APP_ID}.desktop"
install-glib-gschema "${APP_ID}.gschema.xml"
install-prefixed share/revolt "${APP_ID}.gresource" -m644

for file in revolt/*.py ; do
	install-prefixed share/revolt "${file}" -m644
done

for size in 16x16 16x16@2x 24x24 24x24@2x 32x32 64x64 ; do
	install-icon "${APP_ID}" "${size}" apps "icons/${size}/apps/revolt.png"
done
install-icon "${APP_ID}" scalable apps icons/scalable/apps/revolt.svg
install-icon "${APP_ID}" symbolic apps icons/scalable/apps/revolt-symbolic.svg

install-finish
