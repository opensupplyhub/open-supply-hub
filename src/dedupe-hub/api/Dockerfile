FROM python:3.8
 
WORKDIR /usr/local/src

# install python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
 
COPY ./app ./app
COPY ./tests ./tests
