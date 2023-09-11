FROM python:3.10.11-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
RUN apt update -y
RUN apt install nano screen  -y
RUN apt install screen -y

COPY cabspottingdata ./cabspottingdata
COPY tdrive ./tdrive
COPY telecom ./telecom
COPY *.py .

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"