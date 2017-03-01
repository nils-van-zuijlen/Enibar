# Copyright (C) 2014-2017 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2017 Arnaud Levaufre <a2levauf@enib.fr>
#
# This file is part of Enibar.
#
# Enibar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Enibar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Enibar.  If not, see <http://www.gnu.org/licenses/>.


python3 -c 'import sys;(print("Python 3.4 or newer is required") and exit(1)) if sys.version_info < (3, 4) else exit(0)' || exit 1
VENV=".enibar-venv"
DIR=$(dirname "$0")
DEBUG=0
DEV=0

TEMP=`getopt -o d --long dev -- "$@"`
eval set -- "$TEMP"

while true ; do
	case "$1" in
		-d|--dev)
			DEV=1
			shift;;
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done

if [ -e "$DIR/$VENV" ]; then
	PYTHON="../$VENV/bin/python3"
else
	echo ""
	echo "WARNING: The venv does\'nt exist, you should probably"
	echo "update the application by running ./update.sh"
	echo ""
	exit 1
fi

cd $DIR/application


if [[ $DEV == 1 ]]; then
    rustup override set nightly
    cd rapi
    cargo build || exit
    cd ..
    cp rapi/target/debug/librapi.so rapi.so
fi

if [[ ! -e "local_settings.py" ]]; then
    echo ''
    echo 'The local_settings.py file is non existant'
    echo 'You should probably run ./bin/setup.py'
    echo ''
fi


OUT="$($PYTHON -c 'import settings; print(settings.DEBUG)')"
if [[ $? -eq 5 ]]; then
    exit 5
fi

if [[ $(echo $OUT | grep "True" &> /dev/null) ]]; then
    DEBUG="1"
fi

if wmctrl -h &>/dev/null; then
    WIN_ID=$(wmctrl -l | grep -e " Enibar$" | cut -d ' ' -f1 | tail -n1)
fi

if [[ "$WIN_ID" = "" || "$DEBUG" = "0" ]]; then
    /bin/sh -c "$PYTHON -OO main.py"
else
    wmctrl -i -a $WIN_ID
fi

