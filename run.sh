python3 -c 'import sys;(print("Python 3.4 or newer is required") and exit(1)) if sys.version_info < (3, 4) else exit(0)' || exit 1
VENV="enibar-venv"
DIR=$(dirname "$0")

if [ -e "$DIR/$VENV" ]; then
	PYTHON="../$VENV/bin/python3"
else
	echo ''
	echo "WARNING: The venv does\'nt exist, you should probably"
	echo "update the application by running ./update.sh"
	echo ''
	exit 1
fi
cd $DIR
cd application
exec $PYTHON "-OO" "main.py"
