FROM jenkinsci/blueocean

ENV DOCKER_HOST=tcp://docker:2376 \ 
    DOCKER_CERT_PATH=/certs/client \
    DOCKER_TLS_VERIFY=1

EXPOSE 8080:8080
EXPOSE 50000:50000

VOLUME ["/var/jenkins_home", "/certs/client:ro"]