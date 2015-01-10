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

TEMP=`getopt -o tp --long test,pep,no-docker,no-vd -- "$@"`
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
		--no-docker)
			NODOCKER=1
			shift;;
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

	# -- MYSQL --
	if [[ $NODOCKER != 1 ]]; then
		DOCKER_MYSQL_ID=$(docker run -d eijebong/mariadb)
		IP=$(docker inspect $DOCKER_MYSQL_ID | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["NetworkSettings"]["IPAddress"])')
		sed "s/{IP}/${IP}/" ../test/resources/settings/settings_mysql.py > settings.py
		echo "[ .... ] Waiting for db..."
		sleep 30

		mysql --user="root" --password="toor" --host="$IP" < ../db.sql
	else
		mysql --user="root" < ../db.sql
	fi

	# -- TEST --
	rm -f $APPLICATION_DIR/.coverage
	nosetests ../test/*.py -v --with-coverage --cover-package=api || TEST_FAILED=1

	mv settings.py.bak settings.py
fi

rm -f img/coucou.jpg

if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pep8 --exclude=documentation,enibar-venv,.ropeproject --ignore=E501,W391,E128,E124 ../ || TEST_FAILED=1
fi

if [[ $NODOCKER != 1 && $TEST == 1 ]]; then
	docker stop $DOCKER_MYSQL_ID
fi
exit $TEST_FAILED

