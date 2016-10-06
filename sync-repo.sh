#! /bin/bash
#
# sync-repo.sh
# Copyright (C) 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.
#
set -e

LOCAL="$(dirname "$0")/.flatpak-repo/"
REMOTE='aperez@igalia.com:public_html/flatpak/vector-gnome/'

declare -a rsync_command=( rsync -avz --delete --progress )

case $1 in
	push)
		rsync_command+=( "${LOCAL}" "${REMOTE}" )
		;;
	pull)
		rsync_command+=( "${REMOTE}" "${LOCAL}" )
		;;
	*)
		echo "Usage: $0 push|pull" 1>&2
		exit 1
		;;
esac

echo "Running: ${rsync_command[*]}"
exec "${rsync_command[@]}"
