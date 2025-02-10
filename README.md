# Aldrovanda
A samba server honeypot


docker build -t aldrovanda .

docker run -d -p 80:80 -p 139:139 -p 445:445 aldrovanda

- Files uploaded to the unauthenticated share are hashed, encrypted, relocated and the original file is deleted.
- All Samba sessions are closed with a subprocess call to smbcontrol, thusly reducing the window for follow on actions by an intruder.

![terminal](https://github.com/user-attachments/assets/0768d092-1f9b-450f-af19-4a099ffc2bcc)

- The web interface displays a listing of unique hashes, filenames and IP addresses

![web](https://github.com/user-attachments/assets/8a8098e0-c834-417c-af7d-dc9532ef6721)
