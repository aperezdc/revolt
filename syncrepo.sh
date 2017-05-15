#! /bin/bash
#
# sync-repo.sh
# Copyright (C) 2016-2017 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the GPLv3 license.
#
set -e

LOCAL="$(dirname "$0")/.flatpak-repo/"
REMOTE='aperez@perezdecastro.org:/srv/http/flatpak.perezdecastro.org/revolt/'

RSYNC_REPOS=$(type -P ostree-rsync-repos rsync-repos | head -1)
if [[ -z ${RSYNC_REPOS} ]] ; then
	echo "$0: The ostree-rsync-repos (or rsync-repos) tool is not installed."
	echo 'Please install from https://github.com/ostreedev/ostree-releng-scripts'
	echo 'and make sure the tools are in your $PATH'
	exit 1
fi 1>&2

declare -a rsync_command=( "${RSYNC_REPOS}" )

case $1 in
	push)
		rsync_command+=( --src "${LOCAL}" --dest "${REMOTE}" )
		;;
	pull)
		rsync_command+=( --src "${REMOTE}" --dest "${LOCAL}" )
		;;
	*)
		echo "Usage: $0 push|pull" 1>&2
		exit 1
		;;
esac
exec "${rsync_command[@]}"
