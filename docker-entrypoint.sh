#!/bin/bash
set -e

if [ "$1" = 'pyco' ]; then
    export WSGI_APP="pyco:app"
    export PORT=5500
elif [ "$1" = 'admin' ]; then
    export WSGI_APP="pyco_admin:app"
    export PORT=5510
else
  echo 'unknown option, use "pyco" or "admin"'
  exit 1
fi

exec gunicorn -k gevent -b "0.0.0.0:$PORT" --access-logfile - --error-logfile - $WSGI_APP