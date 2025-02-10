
FROM ubuntu:latest

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    samba \
    smbclient \
    sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv

RUN /bin/bash -c "source /app/venv/bin/activate && python3 -m pip install --no-cache-dir -r requirements.txt"

COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /opt/share
RUN chmod -R 777 /opt/share

RUN echo "[share]\n\
   comment = Samba share directory\n\
   path = /opt/share\n\
   read only = no\n\
   writable = yes\n\
   browseable = yes\n\
   guest ok = yes" >> /etc/samba/smb.conf

EXPOSE 80
EXPOSE 139
EXPOSE 445

ENTRYPOINT ["/app/entrypoint.sh"]