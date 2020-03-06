#!/bin/bash

MSG="\nError!"
PYTHON_CONFIGURE_OPTS="--enable-shared" python3 -m venv venv &&\
. ./venv/bin/activate &&\
pip install -r requirements.txt &&\
pyinstaller --onefile putpublic/__init__.py -n putpublic &&\
cp ./dist/putpublic /usr/local/bin/ &&\
MSG="\nSuccess!"
rm -rf dist build *.spec
echo -e $MSG