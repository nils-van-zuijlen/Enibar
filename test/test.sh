# Copyright (C) 2014-2015 Bastien Orivel <b2orivel@enib.fr>
# Copyright (C) 2014-2015 Arnaud Levaufre <a2levauf@enib.fr>
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


TEST_FAILED=0
export USE_VD=1
export TEST_ENIBAR=1
APPLICATION_DIR="application"

TEMP=`getopt -o agp --long api,gui,pep,no-vd -- "$@"`
eval set -- "$TEMP"

# == EXTRACT OPTIONS
while true ; do
	case "$1" in
		-p|--pep)
			PEP=1
			shift;;
		-a|--api)
			API=1
			shift ;;
		-g|--gui)
			GUI=1
			shift ;;
		--no-vd)
			export USE_VD=0
			shift;;
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done


if [[ $API == 1 || $GUI == 1 ]]; then
	# -- BACKUP --
	rm -f img/coucou.jpg
    killall -9 postgres Xvfb
    rm -Rf /tmp/postgres_enibar /tmp/.X1023-lock

    echo "Importing"
    mkdir /tmp/postgres_enibar
    initdb -D /tmp/postgres_enibar -E utf8  -U enibar
    postgres -D /tmp/postgres_enibar -p 2356 -k /tmp/postgres_enibar &>/dev/null &
    sleep 5
    createdb -U enibar -h /tmp/postgres_enibar -p 2356 enibar
    ./migrations.py apply
    cd $APPLICATION_DIR

    if [[ $USE_VD == 1 ]]; then
        SCREEN=$(( ( RANDOM % 1000 )  + 1000 ))
        Xvfb :$SCREEN -screen 0 1600x1200x24+32 &
        XVFB=$!
        export DISPLAY=:$SCREEN
    fi

    echo "Starting tests"
	# -- TEST --
	rm -f .coverage
    if [[ $API == 1 ]]; then
	    nosetests ../test/*api*.py -v --with-coverage --cover-package=api || TEST_FAILED=1
    fi

    if [[ $GUI == 1 ]]; then
	    nosetests ../test/*gui*.py -v --with-coverage --cover-package=gui || TEST_FAILED=1
    fi

    if [[ $USE_VD == 1 ]]; then
        kill $XVFB
    fi

    cd ..
    sleep 2
    rm -Rf /tmp/postgres_enibar
fi

cd $APPLICATION_DIR
rm -f img/coucou.jpg

if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pycodestyle --exclude=documentation,enibar-venv,.ropeproject,utils --ignore=E722,E501,W391,E128,E124 ../ || TEST_FAILED=1
fi

exit $TEST_FAILED

