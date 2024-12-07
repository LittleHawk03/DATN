FROM python:3.12.8-alpine3.19

# Install curl and download kubectl
RUN apk add --no-cache curl bash vim && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

COPY ./manifest_file/requirements.txt /
COPY ./manifest_file/exploit.py /
RUN pip install -r /requirements.txt
ENV K8S_ENVIRONMENT='pod'

CMD ["bash"]