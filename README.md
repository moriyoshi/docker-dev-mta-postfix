# dev-mta-postfix

A simple MTA for development using Postfix

## Features

* Catch-all email address

  Any mails to arbitrary senders can be directed to a single e-mail address

* Gmail XOAUTH2 support

  Thanks to [cyrus-sasl-xoauth2](https://github.com/moriyoshi/cyrus-sasl-xauth2), SASL XOAuth2 authentication is supported out of the box.

## Synopsis

```
docker run 
  -e CATCHALL_EMAIL_ADDRESS=someone@example.com
  -e POSTFIX_RELAY_HOST='[smtp.gmail.com]:587'
  -e POSTFIX_RELAY_TLS=may
  -e POSTFIX_RELAY_AUTH_USER=someone@example.com
  -e POSTFIX_RELAY_AUTH_PASSWORD=credential-such-as-XOAUTH2-token
  moriyoshi/docker-dev-mta-postfix
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

## License

The source codes that originates from this repository are solely licensed under the MIT license.

Other copyrighted materials may be licensed under the different terms.
