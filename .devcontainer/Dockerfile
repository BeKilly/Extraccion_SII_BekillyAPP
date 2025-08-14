# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/python:3.11

ARG DEBIAN_FRONTEND=noninteractive

# Zona horaria y locale (Chile)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata locales && \
    ln -fs /usr/share/zoneinfo/America/Santiago /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    sed -i 's/# es_CL.UTF-8 UTF-8/es_CL.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen es_CL.UTF-8 && \
    update-locale LANG=es_CL.UTF-8 LC_ALL=es_CL.UTF-8

ENV TZ=America/Santiago
ENV LANG=es_CL.UTF-8
ENV LC_ALL=es_CL.UTF-8

# Navegador para Selenium: Chromium + chromedriver (empaquetados juntos)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        fonts-liberation \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Variables para que Selenium encuentre el binario y driver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMIUM_BIN=/usr/bin/chromium
ENV PATH="/usr/lib/chromium:${PATH}"

# Instalar dependencias de Python dentro del contenedor
WORKDIR /workspaces/${localWorkspaceFolderBasename}
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
