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
	msgfmt --check --output-file="$target/$code/LC_MESSAGES/terminal-svg-demo.mo" "$po"
	printf 'built %s\n' "$target/$code/LC_MESSAGES/terminal-svg-demo.mo"
done
