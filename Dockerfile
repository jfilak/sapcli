FROM python:3.10-alpine

RUN pip3 install requests

COPY . /opt/sapcli

RUN cd /opt/sapcli &&\
	python3 -m pip install -r requirements.txt &&\
	dos2unix /opt/sapcli/bin/sapcli &&\
	chmod +x /opt/sapcli/bin/sapcli

ENV PATH="/opt/sapcli/bin:${PATH}"
ENV PYTHONPATH="/opt/sapcli:${PYTHONPATH}"

WORKDIR /var/tmp

ENTRYPOINT ["sapcli"]
