#!/bin/sh
#
# Compile po/*.po into the package locale directories.
# Needs msgfmt, from the gettext package.

set -eu

root=$(cd -- "$(dirname -- "$0")/.." && pwd)
target="$root/src/terminal_svg_demo/locale"

for po in "$root"/po/*.po; do
	[ -e "$po" ] || continue
	code=$(basename "$po" .po)
	mkdir -p "$target/$code/LC_MESSAGES"
	final="$target/$code/LC_MESSAGES/terminal-svg-demo.mo"
	tmp="$final.tmp"

	# Compile to a temporary name: a failed msgfmt leaves no catalogue
	if ! msgfmt --check --output-file="$tmp" "$po"; then
		rm -f "$tmp"
		exit 1
	fi
	mv "$tmp" "$final"
	printf 'built %s\n' "$final"
done
