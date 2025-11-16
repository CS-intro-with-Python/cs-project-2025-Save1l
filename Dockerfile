FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app

ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_RUN_RELOAD=true
# ENV FLASK_DEBUG=1

CMD ["flask", "run"]

