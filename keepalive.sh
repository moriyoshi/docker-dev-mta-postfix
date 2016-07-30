#!/bin/sh
STATE_INI=$1
expires_in=$(python /dev-mta-postfix/oauth2.py "${STATE_INI}" auth) &&
POSTFIX_RELAY_AUTH_PASSWORD=$(python /dev-mta-postfix/oauth2.py "${STATE_INI}" token) /dev-mta-postfix/provision.sh &&
/usr/sbin/postfix reload &&
echo ${expires_in} || echo 30
