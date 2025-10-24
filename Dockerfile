FROM python:3.11
# Our base image, Debian (Linux) with installed Python
WORKDIR /app
# Set /app as workdir
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
# Copy files from . (local) to /app (in image)

#replace <command> with any command which
# you want to execute in image
# you can use several RUN
# example: RUN pip install -r requirements.txt
CMD ["python", "server.py"]