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
	cp settings.py settings.py.bak

	# -- MYSQL --
	if [[ $NODOCKER != 1 ]]; then
		DOCKER_MYSQL_ID=$(docker run -d eijebong/mariadb)
		IP=$(docker inspect $DOCKER_MYSQL_ID | python -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["NetworkSettings"]["IPAddress"])')
		sed "s/{IP}/${IP}/" ../test/resources/settings/settings_mysql.py > settings.py
		echo "[ .... ] Waiting for db..."
		sleep 10

		mysql --user="root" --password="toor" --host="$IP" < ../db.sql
	fi

	# -- TEST --
	python -m unittest discover ../test '*.py' -v || TEST_FAILED=1

	mv settings.py.bak settings.py
fi


if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pep8 --exclude=documentation --ignore=E501,W391,E128,E124 ../ || TEST_FAILED=1
	pylint * --disable=parse-error || TEST_FAILED=1
fi

exit $TEST_FAILED
