FROM python:3.12-alpine

WORKDIR /SongGuess

COPY ./SongGuess /SongGuess/

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
RUN apk add openssl

RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=DE/ST=State/L=City/O=Organization/CN=localhost"

RUN sed -i 's/debug=True/debug=False/' app.py

RUN flask db upgrade

EXPOSE 80
EXPOSE 443

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "1", "--certfile", "cert.pem", "--keyfile", "key.pem"]
