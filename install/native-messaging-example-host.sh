#!/bin/sh

echo "RUN" >>  /tmp/err.log

#checkio webplugin >>/tmp/err.log
cd /Users/oduvan/www/checkio/mission-design/checkio-client/
echo `pwd` >>  /tmp/err.log
echo `python3 --version` >>  /tmp/err.log
/Users/oduvan/anaconda3/bin/python3 web_plugin.py