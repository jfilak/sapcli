FROM python:3.10-alpine

RUN pip3 install requests

COPY . /opt/sapcli

RUN cd /opt/sapcli &&\
	python3 -m pip install -r requirements.txt &&\
	chmod +x /opt/sapcli/sapcli &&\
	echo '#!/bin/sh' > /usr/bin/sapcli &&\
	echo 'python3  /opt/sapcli/sapcli "$@"' >> /usr/bin/sapcli &&\
	chmod +x /usr/bin/sapcli

WORKDIR /var/tmp

ENTRYPOINT ["sapcli"]
