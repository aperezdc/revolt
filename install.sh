#! /bin/bash
#
# install.sh
# Copyright (C) 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.
#

source "$(dirname "$0")/install-functions.sh"
install-setup "$0" "$@"

install-bin riot
install-desktop-file com.igalia.VectorGnome.desktop

for size in 16 32 48 64 128 256 ; do
	install-icon com.igalia.VectorGnome ${size} apps assets/riot-${size}.png
done
install-icon com.igalia.VectorGnome scalable apps assets/riot.svg

install-finish
