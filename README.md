# Aldrovanda
A samba server honeypot

```
docker build -t aldrovanda .
```
```
docker run -d -p 80:80 -p 139:139 -p 445:445 aldrovanda
```

![aldrovanda_diagram](https://github.com/user-attachments/assets/a9230187-05da-4282-b6af-79e771cc785f)

- Files uploaded to the unauthenticated share are hashed, encrypted and relocated. The original file is deleted.
- Encrypted files remain on the system and can be downloaded for later analysis.
- Use the decrypt.py script along with the password established in the configuration file.
- All Samba sessions are closed with a subprocess call to smbcontrol, thusly reducing the window for follow on actions by an intruder.

![terminal](https://github.com/user-attachments/assets/0768d092-1f9b-450f-af19-4a099ffc2bcc)

- The web interface displays a listing of unique hashes, filenames and IP addresses The file listing allows for file retrieval.

![web](https://github.com/user-attachments/assets/8a8098e0-c834-417c-af7d-dc9532ef6721)
