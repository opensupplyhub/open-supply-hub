FROM python:3.11-slim-bookworm
 
WORKDIR /usr/local/src

# install python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
 
COPY . .
