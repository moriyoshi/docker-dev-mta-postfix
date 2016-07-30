# dev-mta-postfix

A simple MTA for development using Postfix

## Features

* Catch-all email address

  Any mails to arbitrary senders can be directed to a single e-mail address

* Gmail XOAUTH2 support

  Thanks to [cyrus-sasl-xoauth2](https://github.com/moriyoshi/cyrus-sasl-xoauth2), SASL XOAuth2 authentication is supported out of the box.

## Synopsis

```
docker run \
  -e CATCHALL_EMAIL_ADDRESS=someone@example.com \
  -e POSTFIX_RELAY_HOST='[smtp.gmail.com]:587' \
  -e POSTFIX_RELAY_TLS=may \
  -e POSTFIX_RELAY_AUTH_USER=someone@example.com \
  -e POSTFIX_RELAY_AUTH_PASSWORD=credential-such-as-XOAUTH2-token \
  moriyoshi/dev-mta-postfix
```

## Environment variables

* CATCHALL_EMAIL_ADDRESS

  ```
  -e CATCHALL_EMAIL_ADDRESS=someone@example.com
  ```
* POSTFIX_RELAY_HOST

  ```
  -e POSTFIX_RELAY_HOST='[smtp.gmail.com]:587'
  ```

* POSTFIX_RELAY_TLS

  ```
  -e POSTFIX_RELAY_TLS=may
  ```

* POSTFIX_RELAY_AUTH_USER

  ```
  -e POSTFIX_RELAY_AUTH_USER=someone@example.com
  ```

* POSTFIX_RELAY_AUTH_PASSWORD

  ```
  -e POSTFIX_RELAY_AUTH_PASSWORD=credential-such-as-XOAUTH2-token
  ```

* POSTFIX_RELAY_HOST_BY_SENDER

  ```
  -e POSTFIX_RELAY_HOST_BY_SENDER='
  someone@example.com	[smtp.gmail.com]:587
  another@example.com	[intranet]:25
  '
  ```

* POSTFIX_RELAY_SASL_MECHANISMS
  ```
  -e POSTFIX_RELAY_SASL_MECHANISMS=login,plain
  ```

  ```
  -e POSTFIX_RELAY_SASL_MECHANISMS=xoauth2
  ```

* OAUTH2_TOKEN_AUTO_REFRESH

  ```
  -e OAUTH2_TOKEN_AUTO_REFRESH=1
  ```

  Setting a non-empty value enables OAuth2 token auto-refresh.


## OAuth2 token auto refreshing

Executing the following outputs the OAuth2 authorization endpoint URL.

```
docker run \
  --rm \
  -e OAUTH2_AUTH_ENDPOINT=https://accounts.google.com/o/oauth2/auth \
  -e OAUTH2_TOKEN_ENDPOINT=https://accounts.google.com/o/oauth2/token \
  -e OAUTH2_SCOPE=mail.google.com \
  -e OAUTH2_CLIENT_ID=***** \
  -e OAUTH2_CLIENT_SECRET=***** \
  -v SOME-DIRECTORY:/dev-mta-postfix/state \
  moriyoshi/dev-mta-postfix auth
```

Get the authorization code by navigating your browser to the URL and put the code to the `[oauth2-state]` in `SOME-DIRECTORY/state.ini` that should have been created by the above.

```
[oauth2]
client_id = *****
client_secret = *****

[oauth2-state]
authorization_code = HERE
```

Then, launch the container like below.

```
docker run \
  -e CATCHALL_EMAIL_ADDRESS=someone@example.com \
  -e POSTFIX_RELAY_HOST='[smtp.gmail.com]:587' \
  -e POSTFIX_RELAY_TLS=may \
  -e POSTFIX_RELAY_AUTH_USER=someone@example.com \
  -e OAUTH2_TOKEN_AUTO_REFRESH=1 \
  -v SOME-DIRECTORY:/dev-mta-postfix/state \
  moriyoshi/dev-mta-postfix
```

## License

The source codes that originate from this repository are solely licensed under the MIT license.

Other copyrighted materials may be licensed under the different terms.
