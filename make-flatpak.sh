#! /bin/bash
set -e

readonly BUILDDIR="$(dirname "$0")/.flatpak-build"
readonly REPODIR="$(dirname "$0")/.flatpak-repo"

cleanup () {
	rm -rf "${BUILDDIR}"
}
trap cleanup EXIT

declare -a buildargs=(
	--sandbox
	--force-clean
	--require-changes
	--repo="${REPODIR}"
	--subject="Revolt $(date +%Y%m%d).$(git describe --always --tags)"
)

if [[ -n ${EMAIL} ]] ; then
	buildargs+=( --gpg-sign="${EMAIL}" )
fi

set -x
exec flatpak-builder "${buildargs[@]}" "${BUILDDIR}" "$@" org.perezdecastro.Revolt.json

