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
