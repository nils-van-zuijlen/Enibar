TEST_FAILED=0
APPLICATION_DIR="application"
cd $APPLICATION_DIR

TEMP=`getopt -o tp --long test,pep,no-docker -- "$@"`
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
	fi

	# -- TEST --
	nosetests ../test/*.py -v --with-coverage --cover-package=api || TEST_FAILED=1

	mv settings.py.bak settings.py
fi

rm -f img/coucou.jpg

if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pep8 --exclude=documentation --ignore=E501,W391,E128,E124 ../ || TEST_FAILED=1
fi

if [[ $NODOCKER != 1 && $TEST == 1 ]]; then
	docker stop $DOCKER_MYSQL_ID
fi
exit $TEST_FAILED

