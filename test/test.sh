TEST_FAILED=0
APPLICATION_DIR="application"
cd $APPLICATION_DIR

TEMP=`getopt -o tp --long test,pep -- "$@"`
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
		--) shift ; break ;;
		*) echo "Internal error!" ; exit 1 ;;
	esac
done


if [[ $TEST == 1 ]]; then
	# -- TEST --
	python -m unittest discover ../test '*.py' -v || TEST_FAILED=1
fi


if [[ $PEP == 1 ]]; then
	# Pep8 Validation
	pep8 --ignore=E501,W391,E128,E124 ../ || TEST_FAILED=1
	pylint * --disable=parse-error || TEST_FAILED=1
fi

exit $TEST_FAILED
