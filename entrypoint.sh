#!/bin/sh
STATE_INI="/dev-mta-postfix/state/state.ini"
WATCHDOG_KEEPALIVE="/dev-mta-postfix/keepalive.sh ${STATE_INI}"
PROVISION="/dev-mta-postfix/provision.sh"
WATCHDOG="/dev-mta-postfix/watchdog.py"
PIDFILE="/var/spool/postfix/pid/master.pid"

case "$1" in
    "")
        "${PROVISION}"
        if [ -n "${OAUTH2_TOKEN_AUTO_REFRESH}" ]; then
            export WATCHDOG_KEEPALIVE
        fi
        exec "${WATCHDOG}" "${PIDFILE}" /usr/sbin/postfix start
        ;;
    "auth")
        (
            echo '[oauth2]'
            [ -n "${OAUTH2_AUTH_ENDPOINT}" ] && echo "auth_endpoint = ${OAUTH2_AUTH_ENDPOINT}"
            [ -n "${OAUTH2_TOKEN_ENDPOINT}" ] && echo "token_endpoint = ${OAUTH2_TOKEN_ENDPOINT}"
            [ -n "${OAUTH2_SCOPE}" ] && echo "scope = ${OAUTH2_SCOPE}"
            echo "client_id = ${OAUTH2_CLIENT_ID}"
            echo "client_secret = ${OAUTH2_CLIENT_SECRET}"
        ) > "${STATE_INI}"
        python /dev-mta-postfix/oauth2.py "${STATE_INI}" init
        ;;
    *)
        exec $@
        ;;
esac
