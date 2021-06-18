#!/usr/bin/env bash

# Build the library documentation and push it to GitHub pages.
#
# Usage: pages.sh <repo> <gh-pages>
#
# <repo>        A directory containing the sources from which the documentation
#               will be generated. In most cases this should be an up to date
#               checkout from `origin/master`.
#
# <gh-pages>    A directory containing a checkout with the `origin/gh-pages`
#               branch.
#
# See also `pages.yml`, which is the primary consumer of this script.

set -o errexit # Fail the script if a command returns non-zero.
set -o nounset # Fail the script if an unset variable is used.

repo_dir=$1
pages_dir=$2

echo "(DEBUG) Starting pages.sh"
source "$HOME/.poetry/env"
poetry install
venv_path=$(poetry env info --path)
echo "(DEBUG) Virtual environment path is ${venv_path}"
source "$venv_path"/bin/activate
echo "(DEBUG) Virtual environment activate"
poetry run make -C "$repo_dir/docs" html
deactivate
echo "(DEBUG) Virtual environment deactivated"
cwd=$(pwd)
echo "(DEBUG) PWD is $cwd"
rm -rf "${pages_dir:?}/"*
cp -r "$repo_dir/docs/build/html/"* "$pages_dir"

# By default GitHub pages treats a site like a Jekyll page and uses Jekyll to
# build the page. Normally this isn't a problem for purely static content as
# that's (mostly) a valid Jekyll page. Jekyll does however ignore files with
# leading underscores, and Sphinx generates directories like `_static/`.
#
# Adding a `.nojekyll` file make GitHub treat the page as purely static files.
touch "$pages_dir/.nojekyll"

git -C "$pages_dir" commit -m "Update GitHub pages" --allow-empty
git -C "$pages_dir" push
