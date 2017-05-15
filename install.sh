#! /bin/bash
#
# install.sh
# Copyright (C) 2016-2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.
#
set -e
shopt -s nullglob

declare -r APP_ID='org.perezdecastro.Revolt'

source "$(dirname "$0")/install-functions.sh"
install-setup "$0" "$@"

install-bin bin/revolt
install-desktop-file "${APP_ID}.desktop"
install-prefixed share/revolt "${APP_ID}.gresource" -m644

install-glib-gschema "${APP_ID}.gschema.xml"
for file in ./[0-9][0-9]_${APP_ID}.gschema.override ; do
	install-glib-gschema "${file}"
done

for file in revolt/*.py ; do
	install-prefixed share/revolt/py/revolt "${file}" -m644
done

for size in 16x16 16x16@2x 24x24 24x24@2x 32x32 64x64 ; do
	install-icon "${APP_ID}" "${size}" apps "icons/${size}/apps/revolt.png"
done
install-icon "${APP_ID}" scalable apps icons/scalable/apps/revolt.svg
install-icon "${APP_ID}" symbolic apps icons/scalable/apps/revolt-symbolic.svg

install-finish
