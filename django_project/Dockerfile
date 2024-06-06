FROM python:alpine

RUN mkdir -p /opt/hasker
WORKDIR /opt/hasker
ADD requirements.txt /opt/hasker
RUN pip install -r requirements.txt
ADD hasker /opt/hasker
ADD run.sh /opt/hasker

CMD ["sh", "run.sh"]
