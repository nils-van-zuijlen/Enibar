# ENIBar

This is a Cafeteria management software.

Its server uses postgresql as database and redis as a synchronisation channel.

The client is made in python an rust, the frontend has been done with Qt5.

It synchronises itself nicely with the website [ENIB/Website](https://github.com/ENIB/Website).

## Installation

ArchLinux is the prefered distribution to run this software.

You should have a redis and a postgresql server configurated on default ports.
You only need these once, they are the only server software.

You should have rustup installed on the PCs you want to install the client.

- Create a postgres user named enibar, with rights to create databases. It can have a password.
- Create a python3.7 virtualenv in folder `.enibar-venv`.
- Install python packages required in `requirements.txt` in that venv.
- Install the cargo toolchain for nightly and stable using rustup. Nightly is used for dev and stable for prod.
- Run `cargo build` with the python venv activated. If you get any compilation errors, please report the issue in this repository.
- Copy the file `target/debug/librapi_py.so` to `application/rapi.so`
- Run the `bin/setup.py` script and answer the prompts. If it is the first time you run it, you shall configure the postgres database py answering `y` when prompted.
- Run `bin/migrations.py`. You must run it at every update you make to the software. You cannot run it too many times, it will only do the needed work.
- To run the software, just run the `run.sh` script. It takes care of everything, even the venv.

### IMPORTANT

You should not allow modification to the software for any user.
Some files are highly sensitive as they may disable all password verification.
A good value for the rights is rwxr-xr-x for the executables and rw-r--r-- for the other files.
They normally have these rights. Please ensure that the owner of the files is a well protected account.
