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
APPLICATION_DIR="application"
cd $APPLICATION_DIR

TEMP=`getopt -o tp --long test,pep,no-vd -- "$@"`
eval set -- "$TEMP"

# == EXTRACT OPTIONS
while true ; do
	case "$1" in
		-p|--pep)
			PEP=1
			shift;;
		-t|--test)
			TEST=1
			shift ;;
		--no-vd)
			export USE_VD=0
			shift;;
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done


if [[ $TEST == 1 ]]; then
	# -- BACKUP --
	rm -f img/coucou.jpg
	cp settings.py settings.py.bak

    rm -Rf /tmp/enibar
    mkdir -p /tmp/enibar
    mysql_install_db --basedir=/usr --datadir=/tmp/enibar
    mysqld --no-defaults --pid-file=/tmp/mysql.pid -P 4569 --datadir /tmp/enibar/ --socket=/tmp/mysql.socket &
    sleep 5;
    echo "Importing"
	# -- MYSQL --
	mysql --socket=/tmp/mysql.socket --user="root" --port 4569 < ../db.sql
    export TEST_ENIBAR=1
	# -- TEST --
	rm -f .coverage
	nosetests ../test/*.py -v --with-coverage --cover-package=api,gui || TEST_FAILED=1

	mv settings.py.bak settings.py
    kill `cat /tmp/mysql.pid`
fi

rm -f img/coucou.jpg

if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pycodestyle --exclude=documentation,enibar-venv,.ropeproject,utils --ignore=E501,W391,E128,E124 ../ || TEST_FAILED=1
fi

exit $TEST_FAILED

