FROM alpine:3.4
RUN apk update && apk add python postfix py-pip cyrus-sasl-dev libc-dev gcc make autoconf automake libtool
ADD https://github.com/moriyoshi/cyrus-sasl-xoauth2/archive/v0.1.tar.gz /tmp/
WORKDIR /tmp
RUN tar xf v0.1.tar.gz && cd cyrus-sasl-xoauth2-0.1 && ./autogen.sh && ./configure --with-cyrus-sasl=/usr && make install
RUN apk del cyrus-sasl-dev libc-dev gcc make autoconf automake libtool
RUN rm -rf cyrus-sasl-xoauth2-0.1 v0.1.tar.gz 
WORKDIR /
RUN pip install jinja2
COPY ./provision /tmp/provision
COPY ./watchdog.py ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD [""]
