#! /bin/bash
#
# install.sh
# Copyright (C) 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.
#

install_log_file=''
install_destdir=''
install_prefix='/usr/local'
install_pretend=false
install_mode='install'
install_help='Usage: %s [--install | --uninstall | --update] [options...]
Operation modes:

   --install, -I     Run in installation mode.
   --uninstall, -D   Run in uninstallation mode.
   --update, -U      Run in update mode.

Options:

   --pretend, -n     Do not perform actions, only print them. The output is
                     suitable to be passed back to the shell as a script.
   --log-file=PATH   Log installed files to a text file at PATH. When running
                     in uninstall or update mode, the list of files previously
                     installed is taken from the log file, and then it is
                     updated with the new list of installed files.
   --prefix=PATH     Installation prefix (default: /usr/local).
   --destdir=PATH    Installation destination directory, useful for creating
                     distribution packages (default: none).
   --help, -h        Show this help message.

'

set -e

# install-setup "$0" "$@"
install-setup () {
	local arg0=$1
	shift
	for option in "$@" ; do
		case "${option}" in
			--uninstall | -D)
				install_mode=uninstall
				;;
			--install | -I)
				install_mode=install
				;;
			--update | -U)
				install_mode=update
				;;
			--pretend | -n)
				install_pretend=true
				;;
			--log-file=*)
				install_log_file=${option#*=}
				;;
			--destdir=*)
				install_destdir=${option#*=}
				;;
			--prefix=*)
				install_prefix=${option#*=}
				;;
			--help | -h)
				printf "${install_help}" "${arg0}"
				exit 0
				;;
		esac
	done

	if [[ -n ${install_log_file} ]] ; then
		if [[ ${install_mode} != install ]] ; then
			# Remove contents listed in the log file
			if [[ -r ${install_log_file} ]] ; then
				local path
				while read -r path ; do
					if ${install_pretend} ; then
						echo "rm -f '${path}'"
					else
						install-show REMOVE "${path}"
						rm -f "${install_destdir}${path}"
					fi
				done < "${install_log_file}"
			fi
			if [[ ${install_mode} = uninstall ]] ; then
				exit 0
			else
				# Make sure the rest of the script runs in installation mode.
				install_mode=install
			fi
		fi

		# Truncate the log file
		${install_pretend} || : > "${install_log_file}"
	fi
}

# install-show <INSTALL | REMOVE> <destination>
install-show () {
	local prepend="[[1;1m$1[0;0m] "
	if [[ -n ${install_destdir} ]] ; then
		prepend="[[1;1m$1[0;0m] [33m${install_destdir}[0;0m"
	fi
	echo "${prepend}$2"
}

# install-exec <source> <destination> [install-options...]
install-exec () {
	local src=$1
	local dst=$2
	shift 2
	case ${INSTALL_EXEC_MODE:-${install_mode}} in
		install)
			if ${install_pretend} ; then
				echo "install -D $* '${src}' '${install_destdir}${dst}'"
			else
				if [[ -n ${install_log_file} ]] ; then
					echo "${dst}" >> "${install_log_file}"
				fi
				install-show INSTALL "${dst}"
				install -D "$@" "${src}" "${install_destdir}${dst}"
			fi
			;;
		uninstall)
			if ${install_pretend} ; then
				echo "rm -f '${dst}'"
			else
				install-show REMOVE "${dst}"
				rm -f "${install_destdir}${dst}"
			fi
			;;
		update)
			INSTALL_EXEC_MODE=uninstall install-exec "${src}" "${dst}" "$@"
			INSTALL_EXEC_MODE=install   install-exec "${src}" "${dst}" "$@"
			;;
	esac
}

# install-prefixed <prefix-relative-path> <filename> [install-options...]
install-prefixed () {
	local relpath=$1
	local filename=$2
	shift 2
	install-exec "${filename}" "${install_prefix}/${relpath}/$(basename "${filename}")" "$@"
}

# install-icon <name> <size> <category> <file> [theme]
# TODO: Make this use install-prefixed, and change that to allow passing
#       destination file names.
install-icon () {
	local ext=${4#*.}
	install-exec "$4" "${install_prefix}/share/icons/${5:-hicolor}/${2}x${2}/$3/$1.${ext}" -m644
}

# install-bin <filename> [install-options...]
# install-desktop-file <filename> [install-options...]
install-bin () { install-prefixed bin "$@" -m755 ; }
install-desktop-file () { install-prefixed share/applications "$@" -m644 ; }
