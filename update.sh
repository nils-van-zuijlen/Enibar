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


python3 -c 'import sys;(print("Python 3.6 or newer is required") and exit(1)) if sys.version_info < (3, 6) else exit(0)' || exit 1
VENV="enibar-venv"
VENV_COMMAND="pyvenv"

mv application/settings.py settings.py.bak
git pull origin master || {
	echo "Failed to update."
	mv settings.py.bak application/settings.py
	exit 1
}
mv settings.py.bak application/settings.py

if [ -e "$VENV" ]; then
	echo 'Trying to upgrade the venv'
	$VENV_COMMAND --upgrade "$VENV"

	 . "$VENV/bin/activate"
	 echo 'Updating dependencies'
	pip install -r requirements.txt
	cp -R /usr/lib/python3.6/site-packages/PyQt5 $VENV/lib/python3.6/site-packages/  || {
		echo ''
		echo 'You have to install PyQt5 manually'
		echo ''
	}
	cp -R /usr/lib/python3.6/site-packages/sip.so $VENV/lib/python3.6/site-packages/ || {
		echo ''
		echo 'You have to install sip manually'
		echo ''
	}
else
	 echo 'Creating the venv'
	 $VENV_COMMAND "$VENV"

	 . "$VENV/bin/activate"

	pip install -r "requirements.txt" --upgrade
	cp -R /usr/lib/python3.6/site-packages/PyQt5 $VENV/lib/python3.6/site-packages/  || {
		echo ''
		echo 'You have to install PyQt5 manually'
		echo ''
	}
	cp -R /usr/lib/python3.6/site-packages/sip.so $VENV/lib/python3.6/site-packages/ || {
		echo ''
		echo 'You have to install sip manually'
		echo ''
	}
fi

