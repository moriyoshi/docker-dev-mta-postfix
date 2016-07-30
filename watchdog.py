#!/usr/bin/python

from __future__ import print_function
import errno
import os
import sys
import subprocess
import traceback
from time import time, sleep
from signal import *
from socket import *
from select import select, error as SelectError

cont = [True]
keepalive = os.environ.get('WATCHDOG_KEEPALIVE')
keepalive_interval = [0]
pidfile = sys.argv[1]
args = sys.argv[2:]
timeout = 30

lfd = socket(AF_UNIX, SOCK_DGRAM, 0)
lfd.bind('/dev/log')

t = [0]
pid = [None]

if hasattr(os, 'getpgid'):
    def killgrp(pid, sig):
        pgid = os.getpgid(pid)
        os.killpg(pgid, sig)
else:
    def killgrp(pid, sig):
        os.kill(pid, sig)

def c0():
    t[0] = time()
    signal(SIGINT, SIG_IGN)
    signal(SIGTERM, SIG_IGN)

def c1():
    try:
        pid[0] = int(open(pidfile).read().strip())
    except Exception as e:
        pass
    if pid[0]:
        print("process launched as pid %d." % pid[0])
        signal(SIGINT, stop)
        signal(SIGTERM, stop)
        t[0] = time()
        return c2
    else:
        if time() - t < timeout:
            print("waiting for process to launch...")
            return c1
        else:
            print("process did not start up in %d seconds" % timeout)
            return stop

def c2():
    try:
        s = os.waitpid(pid[0], os.WNOHANG)
    except:
        pass
    if s[0] == 0:
        if keepalive and keepalive_interval[0] >= 0:
            if time() - t[0] >= keepalive_interval[0]:
                t[0] = time()
                try:
                    sp = subprocess.Popen(keepalive, stdout=subprocess.PIPE, shell=True)
                    o, _ = sp.communicate()
                    o = o.strip()
                    if o:
                        i = None
                        try:
                            i = int(o)
                        except:
                            pass
                        if i is None or i <= 0:
                            print("keepalive process returned wrong value: %s" % o)
                            keepalive_interval[0] = -1
                        keepalive_interval[0] = i
                        print("keepalive interval: %d" % keepalive_interval[0])
                    else:
                        keepalive_interval[0] = -1
                except:
                    traceback.print_exc()
                    keepalive_interval[0] = -1
        return c2
    pid[0] = None
    return stop

def c3():
    signal(SIGTERM, stop2)
    signal(SIGINT, stop2)
    if os.path.exists(pidfile):
        os.kill(pid[0], SIGTERM)
        t[0] = time()
        return c4
    else:
        pid[0] = None
        return stop

def c4():
    print("terminating process...")
    try:
        s = os.waitpid(pid[0], os.WNOHANG)
    except:
        pass

    if s[0] == 0:
        if time() - t[0] >= timeout:
            print("process did not stop in %d second" % timeout)
            return stop
        return c4
    else:
        pid[0] = None
        return stop

def stop(sig, frame):
    print("signal %d received" % sig)
    do_it[0] = c3

def stop2(sig, frame):
    do_it[0] = stop


do_it = [c1]

try:
    subprocess.call(args)
    while True:
        do_it[0] = do_it[0]()
        if do_it[0] is stop:
            break
        try:
            r, _, _ = select([lfd], [], [], 1)
            if r:
                pl, addr = lfd.recvfrom(4096)
                sys.stdout.write(pl)
                sys.stdout.flush()
        except SelectError as e:
            if e.args[0] != errno.EINTR:
                traceback.print_exc()
                do_it[0] = c3
finally:
    try:
        lfd.close()
    except:
        traceback.print_exc()
    if pid[0]:
        killgrp(pid[0], SIGKILL)
        print("process killed")
        sys.exit(1)
    else:
        print("process terminated")
