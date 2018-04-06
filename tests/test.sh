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
TEST=0
export USE_VD=1
export TEST_ENIBAR=1
export DATABASE_HOST="127.0.0.1"
export DATABASE_PORT=2356
export DATABASE_USER="enibar"
export DATABASE_URL="postgres://$DATABASE_USER@$DATABASE_HOST:$DATABASE_PORT/enibar"
cd $(dirname $0)
APPLICATION_DIR="../application"

TEMP=`getopt -o agrp --long api,gui,rust,pep,no-vd -- "$@"`
eval set -- "$TEMP"

# == EXTRACT OPTIONS
while true ; do
	case "$1" in
		-p|--pep)
			PEP=1
			shift;;
		-a|--api)
			API=1
            TEST=1
			shift ;;
		-g|--gui)
			GUI=1
            TEST=1
			shift ;;
        -r|--rust)
            RUST=1
            TEST=1
            shift ;;
		--no-vd)
			export USE_VD=0
			shift;;
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done

cd ..
if [[ $TEST -eq 1 ]]; then
	# -- BACKUP --
    killall -u $USER -q -9 postgres Xvfb
    rm -Rf /tmp/postgres_enibar /tmp/.X1023-lock

	rustup update

    echo "Importing"
    mkdir /tmp/postgres_enibar
    initdb -D /tmp/postgres_enibar -E utf8  -U $DATABASE_USER
    postgres -D /tmp/postgres_enibar -h $DATABASE_HOST -p $DATABASE_PORT -k /tmp/postgres_enibar &>/dev/null &
    sleep 5
    createdb -U $DATABASE_USER -h $DATABASE_HOST -p $DATABASE_PORT enibar

    CARGO_INCREMENTAL=0 cargo build --all --release || exit 1
    cp target/release/librapi_py.so application/rapi.so
    cd bin

    if [[ -e "$APPLICATION_DIR/local_settings.py" ]]; then
        mv $APPLICATION_DIR/local_settings.py $APPLICATION_DIR/local_settings.py.bak
    fi
    echo -e "DEBUG=False\nIMG_BASE_DIR='img/'\nMAX_HISTORY=5\nREDIS_HOST='127.0.0.1'\nREDIS_PASSWORD=None" > $APPLICATION_DIR/local_settings.py

    ./migrations.py apply

    cd $APPLICATION_DIR

    if [[ $USE_VD == 1 ]]; then
        SCREEN=$(( ( RANDOM % 1000 )  + 1000 ))
        Xvfb :$SCREEN -screen 0 1600x1200x24+32 &
        XVFB=$!
        export DISPLAY=:$SCREEN
    fi

    echo "Starting tests"
	rm -f .coverage

	# -- TEST --
    if [[ $API == 1 ]]; then
	    nosetests ../tests/*api*.py -v --with-coverage --cover-package=api || TEST_FAILED=1
    fi

    if [[ $GUI == 1 ]]; then
	    nosetests ../tests/*gui*.py -v --with-coverage --cover-package=gui test_search_by|| TEST_FAILED=1
    fi

    if [[ $RUST == 1 ]]; then
        cd $APPLICATION_DIR/rapi
        cargo test --all || TEST_FAILED=1
        cd ..
    fi

    if [[ $USE_VD == 1 ]]; then
        kill $XVFB
    fi

    if [[ -e "$APPLICATION_DIR/local_settings.py.bak" ]]; then
        mv $APPLICATION_DIR/local_settings.py.bak $APPLICATION_DIR/local_settings.py
    fi
    sleep 2
    rm -Rf /tmp/postgres_enibar
fi

cd $(dirname $0)
cd $APPLICATION_DIR
rm -f img/coucou.jpg

if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pycodestyle --exclude=documentation,.enibar-venv,.ropeproject,utils --ignore=E722,E501,W391,E128,E124,W605,W504 . || TEST_FAILED=1
fi

exit $TEST_FAILED

