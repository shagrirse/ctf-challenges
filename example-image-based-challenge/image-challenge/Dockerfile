FROM python:3.7-slim-buster

RUN mkdir "/opt/pwn-challenge"
COPY ./src/* "/opt/pwn-challenge/"
RUN pip install -r "/opt/pwn-challenge/requirements.txt"
WORKDIR "/opt/pwn-challenge/"
RUN chmod +x serve.sh server.py

EXPOSE 8080
CMD ./serve.sh
