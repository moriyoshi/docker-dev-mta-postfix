#!/usr/bin/python

from __future__ import print_function
import sys
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urlencode, urljoin
from six.moves.configparser import SafeConfigParser, NoOptionError
import json

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
DEFAULT_SCOPE = 'https://mail.google.com/'
DEFAULT_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
DEFAULT_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'

class ApplicationError(Exception):
    pass

def load(f):
    p = SafeConfigParser()
    p.read(f)
    if not p.has_section('oauth2'):
        p.add_section('oauth2')
    if not p.has_section('oauth2-state'):
        p.add_section('oauth2-state')
    return p

def save(p, f):
    h = open(f, 'w')
    try:
        p.write(h)
    finally:
        h.close()

def fetch(url, params=None):
    print("sending request to %s..." % url, file=sys.stderr)
    u = urlopen(url, data=params and urlencode(params))
    try:
        return json.load(u)
    finally:
        u.close()

def get_value(p, section, option):
    try:
        return p.get(section, option)
    except NoOptionError:
        return None

def do(state_file, subcommand=None):
    state = load(state_file)
    oauth2_client_id = get_value(state, 'oauth2', 'client_id')
    oauth2_client_secret = get_value(state, 'oauth2', 'client_secret')

    if not oauth2_client_id or not oauth2_client_secret:
        raise ApplicationError("both client_id and client_secret must be specified")

    if subcommand == 'init':
        auth_endpoint = get_value(state, 'oauth2', 'auth_endpoint') or DEFAULT_AUTH_ENDPOINT
        scope = get_value(state, 'oauth2', 'scope') or DEFAULT_SCOPE
        params = {
            'client_id': oauth2_client_id,
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            }
        print(urljoin(auth_endpoint, '?' + urlencode(params)))
    elif subcommand == 'token':
        access_token = get_value(state, 'oauth2-state', 'access_token')
        if access_token is None:
            raise ApplicationError('no access token is granted')
        print(access_token)
    elif subcommand is None or subcommand == 'auth':
        token_endpoint = get_value(state, 'oauth2', 'token_endpoint') or DEFAULT_TOKEN_ENDPOINT
        authorization_code = get_value(state, 'oauth2-state', 'authorization_code')
        refresh_token = get_value(state, 'oauth2-state', 'refresh_token')
        params = {'client_id': oauth2_client_id, 'client_secret': oauth2_client_secret}
        if authorization_code is not None:
            params['code'] = authorization_code
            params['redirect_uri'] = REDIRECT_URI
            params['grant_type']= 'authorization_code'
            authorization_code = None
            state.remove_option('oauth2-state', 'authorization_code')
        elif refresh_token is not None:
            params['refresh_token'] = refresh_token
            params['grant_type']= 'refresh_token'
        else:
            raise ApplicationError("Neither authorization_code nor refresh_token is specified")
        result = fetch(token_endpoint, params)
        access_token = result['access_token']
        if 'refresh_token' in result:
            refresh_token = result['refresh_token']
        expires_in = result['expires_in']
        state.set('oauth2-state', 'access_token', access_token)
        state.set('oauth2-state', 'refresh_token', refresh_token)
        if expires_in:
            state.set('oauth2-state', 'expires_in', str(expires_in))
        save(state, state_file)
        print(expires_in or '')

if __name__ == '__main__':
    try:
        do(*sys.argv[1:])
    except ApplicationError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)

