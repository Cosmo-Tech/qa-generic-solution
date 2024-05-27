FROM python:latest
LABEL authors="afossart"

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY code /pkg/share/code

ENV CSM_RUN_TEMPLATE_ID=run

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

ENTRYPOINT ["entrypoint.py"]