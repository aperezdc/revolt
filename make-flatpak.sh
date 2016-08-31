#! /bin/bash
set -e

readonly NAME='com.igalia.VectorGnome'
readonly BUILDDIR="$(dirname "$0")/.flatpak-build"
readonly REPODIR="$(dirname "$0")/.flatpak-repo"
readonly GNOMEVER='3.20'

cleanup () {
	rm -rf "${BUILDDIR}" "${REPODIR}"
}
trap cleanup EXIT


flatpak build-init "${BUILDDIR}" "${NAME}" \
	org.gnome.Sdk org.gnome.Platform "${GNOMEVER}"

flatpak build "${BUILDDIR}" ./install.sh --install --prefix=/app --destdir=/
flatpak build-finish "${BUILDDIR}" \
	--device=dri \
	--share=network \
	--share=ipc \
	--socket=x11 \
	--socket=pulseaudio \
	--socket=session-bus \
	--own-name="${NAME}" \
	--talk-name=org.freedesktop.Notifications \
	--talk-name=org.gtk.Notifications \
	--command=vector
flatpak build-export "${REPODIR}" "${BUILDDIR}"

if [[ -n ${EMAIL} ]] ; then
	flatpak build-sign --gpg-sign="${EMAIL}" "${REPODIR}" "${NAME}"
fi

flatpak build-bundle "${REPODIR}" "${NAME}.flatpak" "${NAME}"
