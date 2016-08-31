#! /bin/bash
#
# install.sh
# Copyright (C) 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.
#

source "$(dirname "$0")/install-functions.sh"
install-setup "$0" "$@"

install-bin vector
install-desktop-file com.igalia.VectorGnome.desktop

for size in 32 48 64 128 ; do
	install-icon com.igalia.VectorGnome ${size} apps assets/icon-${size}.png
done

install-finish
