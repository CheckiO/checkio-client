#!/bin/sh

echo "RUN" >>  /tmp/err.log

#checkio webplugin >>/tmp/err.log
cd /Users/oleksandrliabakh/www/checkio/mission-design/checkio-client/checkio_client
/usr/local/bin/python3 web_plugin.py 2>/tmp/err.log