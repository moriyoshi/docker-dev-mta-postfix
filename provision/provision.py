#!/usr/bin/python

import re
import os
import subprocess
import jinja2

def get_postconf(args):
    s = subprocess.Popen(args, stdout=subprocess.PIPE)
    try:
        retval = dict((k.strip(), v.strip()) for k, _, v in (l.partition('=') for l in s.stdout))
    finally:
        s.stdout.close()
        s.wait()
    return retval

def split_by_commas(v):
    v = v.strip()
    if not v:
        return []
    return re.split(r'\s*,\s*|\s+', v)

def split_into_pairs(v):
    retval = []
    for l in v.split("\n"):
        pair = re.split(r'\t+', l.strip(), 2)
        if len(pair) == 1:
            pair = [pair[0], '']
        retval.append(tuple(pair))
    return retval

POSTMAP = os.environ.get('POSTMAP', '/usr/sbin/postmap')
POSTALIAS = os.environ.get('POSTMAP', '/usr/sbin/postalias')
POSTCONF = os.environ.get('POSTCONF', '/usr/sbin/postconf')

templates = [
    ('templates/header_checks.j2', '/etc/postfix/header_checks', POSTMAP, None),
    ('templates/main.cf.j2', '/etc/postfix/main.cf', None, None),
    ('templates/sasl_passwd.j2', '/etc/postfix/sasl_passwd', POSTMAP, lambda vars: vars.get('postfix_relay_auth_user')),
    ('templates/sender_dependent_relayhosts.j2', '/etc/postfix/sender_dependent_relayhosts', None, lambda vars: vars.get('postfix_relay_host_by_sender')),
    ('templates/virtual.j2', '/etc/postfix/virtual', POSTMAP, lambda vars: vars.get('catchall_email_address')),
    ('templates/aliases.j2', '/etc/aliases', POSTALIAS, lambda vars: vars.get('postfix_aliases')),
    ]

postconf = get_postconf([POSTCONF, '-d'])
destdir = os.environ.get('DESTDIR', '')

vars = {}

catchall_email_address = os.environ.get('CATCHALL_EMAIL_ADDRESS')
postfix_relay_host = os.environ.get('POSTFIX_RELAY_HOST')
postfix_relay_tls = os.environ.get('POSTFIX_RELAY_TLS')
postfix_authorized_networks = split_by_commas(postconf['mynetworks']) + split_by_commas(os.environ.get('POSTFIX_AUTHORIZED_NETWORKS', ''))
postfix_relay_auth_user = os.environ.get('POSTFIX_RELAY_AUTH_USER')
postfix_relay_auth_password = os.environ.get('POSTFIX_RELAY_AUTH_PASSWORD', '')
postfix_relay_host_by_sender = split_into_pairs(os.environ.get('POSTFIX_RELAY_HOST_BY_SENDER', ''))
postfix_relay_sasl_mechanisms = split_by_commas(os.environ.get('POSTFIX_RELAY_SASL_MECHANISMS', ''))
postfix_aliases = split_into_pairs(os.environ.get('POSTFIX_ALIASES', ''))

if catchall_email_address:
    vars['catchall_email_address'] = catchall_email_address
if postfix_relay_host:
    vars['postfix_relay_host'] = postfix_relay_host
if postfix_relay_tls:
    vars['postfix_relay_tls'] = postfix_relay_tls
if postfix_authorized_networks:
    vars['postfix_authorized_networks'] = postfix_authorized_networks
if postfix_relay_auth_user:
    vars['postfix_relay_auth_user'] = postfix_relay_auth_user
if postfix_relay_auth_password:
    vars['postfix_relay_auth_password'] = postfix_relay_auth_password
if postfix_relay_host_by_sender:
    vars['postfix_relay_host_by_sender'] = postfix_relay_host_by_sender
if postfix_relay_sasl_mechanisms:
    vars['postfix_relay_sasl_mechanisms'] = postfix_relay_sasl_mechanisms
if postfix_aliases:
    vars['postfix_aliases'] = postfix_aliases

env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))

for src, dest, touch, cond in templates:
    if cond and not cond(vars):
        continue
    if destdir:
        dest = destdir + '/' + dest
    leading_dir = os.path.dirname(dest)
    if not os.path.exists(leading_dir):
        os.makedirs(leading_dir)
    t = env.get_template(src)
    open(dest, 'w').write(t.render(vars))
    if touch is not None:
        subprocess.call([touch, dest])

if not os.exists("/var/mail"):
    os.makedirs("/var/mail")
