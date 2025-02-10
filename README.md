# Aldrovanda
A samba server honeypot


docker build -t aldrovanda .

docker run -d -p 80:80 -p 139:139 -p 445:445 aldrovanda
