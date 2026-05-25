FROM python:3.10

WORKDIR /usr/local/src

COPY ./requirements.txt ./requirements.txt
RUN echo 'cython<3' > /tmp/constraints.txt \
    && PIP_CONSTRAINT=/tmp/constraints.txt pip install --no-cache-dir --upgrade -r requirements.txt \
    && rm /tmp/constraints.txt

COPY ./app ./app
COPY ./tests ./tests
