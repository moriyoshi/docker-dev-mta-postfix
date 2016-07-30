FROM alpine:3.4
RUN apk update && apk add ca-certificates python postfix py-pip cyrus-sasl-dev libc-dev gcc make autoconf automake libtool
ADD https://github.com/moriyoshi/cyrus-sasl-xoauth2/archive/v0.1.tar.gz /tmp/
WORKDIR /tmp
RUN tar xf v0.1.tar.gz && cd cyrus-sasl-xoauth2-0.1 && ./autogen.sh && ./configure --with-cyrus-sasl=/usr && make install
RUN apk del cyrus-sasl-dev libc-dev gcc make autoconf automake libtool
RUN rm -rf cyrus-sasl-xoauth2-0.1 v0.1.tar.gz 
WORKDIR /
RUN pip install jinja2 six
RUN mkdir -p /dev-mta-postfix/state
COPY ./provision /dev-mta-postfix/provision
COPY ./watchdog.py ./oauth2.py ./entrypoint.sh ./keepalive.sh ./provision.sh /dev-mta-postfix/
VOLUME ["/var/spool/postfix", "/dev-mta-postfix/state"]
ENTRYPOINT ["/dev-mta-postfix/entrypoint.sh"]
CMD [""]
