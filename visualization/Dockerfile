FROM julia:latest

RUN apt-get update && apt-get install -y  \
    apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    vim \ 
    nano \
 && cd /usr/local/bin \
 && ln -s /usr/bin/python3 python \
 && rm -rf /var/lib/apt/lists/* 

# Create a virtual environment and install pip packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install julia
RUN python3 -c "import julia; julia.install()"




COPY ./apache-flask.conf /etc/apache2/sites-available/apache-flask.conf
RUN a2ensite apache-flask
RUN a2enmod headers

# Copy over the wsgi file
COPY ./apache-flask.wsgi /var/www/apache-flask/apache-flask.wsgi


RUN a2dissite 000-default.conf
RUN a2ensite apache-flask.conf

# LINK apache config to docker logs.
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log


COPY ./requirements.txt /var/www/apache-flask
COPY ./docker_start.sh /var/www/apache-flask
RUN pip3 install -r /var/www/apache-flask/requirements.txt


RUN pip3 install --upgrade pandas
RUN python3 -c "import julia; julia.install()"
RUN julia -e 'import Pkg;Pkg.add("DataFrames")'
RUN julia -e 'import Pkg;Pkg.add("DifferentialEquations")'
RUN julia -e 'import Pkg;Pkg.add("CSV")'
RUN julia -e 'import Pkg;Pkg.add("DelimitedFiles")'

ENV PORT 80
EXPOSE 80
ENV PYTHONPATH "${PYTHONPATH}:/var/www/apache-flask/app"
WORKDIR /var/www/apache-flask
# ENTRYPOINT
ENTRYPOINT /var/www/apache-flask/docker_start.sh

