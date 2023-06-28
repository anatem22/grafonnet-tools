# Install required libraries 
FROM /docker-hub/golang:1.11.1-alpine AS builder

ARG HTTPS_PROXY=$HTTPS_PROXY
ARG HTTP_PROXY=$HTTPS_PROXY


RUN HTTP_PROXY=$HTTP_PROXY apk add --no-cache git=2.18.4-r0 build-base=0.5-r1 && \
    rm -rf /var/lib/apt/lists/* 

RUN HTTP_PROXY=$HTTP_PROXY git clone https://github.com/google/jsonnet.git && \
    make -C jsonnet 
    
RUN HTTP_PROXY=$HTTP_PROXY go get github.com/jsonnet-bundler/jsonnet-bundler/cmd/jb && \
    jb init && \
    jb install https://github.com/grafana/grafonnet-lib/grafonnet

# Create image for dashboard generation
FROM /docker-hub/python:3.10-alpine

ARG HTTPS_PROXY=$HTTPS_PROXY
ARG HTTP_PROXY=$HTTPS_PROXY

WORKDIR /dashboards

COPY *.py requirements.txt .
RUN chmod a+x grafonnet-gen.py
RUN mkdir -p /dashboards/templates
COPY ./templates/* /dashboards/templates

RUN HTTP_PROXY=$HTTP_PROXY apk add --no-cache libstdc++ ca-certificates curl vim nano mc git curl bash jq py3-pip
RUN pip3 install --no-cache-dir --upgrade pip && pip install --no-cache-dir PyYAML Jinja2 httplib2 urllib3 simplejson requests
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /go/vendor vendor
COPY --from=builder /go/jsonnet/jsonnet /usr/local/bin/
COPY ./configs/* /dashboards/

RUN chmod a+x main.py
USER 1001
CMD [ "./main.py" ]

ENV JSONNET_PATH=/dashboards/vendor

#CMD [ "jsonnet", "-" ]
#CMD [ "chmod -R a+rwx /dashboards/*" ]
