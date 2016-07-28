#!/bin/sh
case "$1" in
    "")
        (cd /tmp/provision && python provision.py)
        exec python /watchdog.py /var/spool/postfix/pid/master.pid /usr/sbin/postfix start
        ;;
    *)
        exec $@
        ;;
esac
