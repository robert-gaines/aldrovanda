from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from smb.SMBConnection import SMBConnection
from datetime import datetime
from src.db import Database
import subprocess
import logging
import hashlib
import yaml
import sys
import os
import re

logging.basicConfig(level=logging.INFO)

class Monitor:
    def __init__(self):
        self.share_name = ''
        self.sessions = []
        self.username = ''
        self.password = ''
        self.client = ''
        self.host = ''
        self.key = ''
        self.iv = os.urandom(16)
        self.db = Database()
        self.db.create_table()
        self.load_config()
        

    def load_config(self) -> None:
        try:
            main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(main_dir, 'config', 'share.yaml')
            if not os.path.exists(config_path):
                logging.error(f"Config file not found at path: {config_path}")
                sys.exit()
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                config = config["share"]
                self.share_name = config["share_name"]
                self.username = config["username"]
                self.password = config["password"]
                self.client = config["client"]
                self.ntlmv2 = config["ntlmv2"]
                self.host = config["server"]
                self.key = config["key"].encode('utf-8')
                if len(self.key) not in [16, 24, 32]:
                    logging.error("Invalid key size for AES. Key must be 16, 24, or 32 bytes long.")
                    sys.exit()
                self.connection = ''
        except FileNotFoundError:
            logging.exception("Share config file not found.")
            sys.exit()

    def connect(self) -> object:
        try:
            self.connection = SMBConnection(self.username,
                                            self.password,
                                            self.client,
                                            self.host,
                                            use_ntlm_v2=self.ntlmv2)
            assert self.connection.connect(self.host, 139)
        except Exception as e:
            logging.exception("Exception: {0}".format(e))

    def enumerate_share(self) -> None:
        files = self.connection.listPath(self.share_name, '/')
        for file in files:
            if file.isDirectory:
                continue
            full_path = os.path.join(self.share_name, file.filename)
            logging.info(f"File: {full_path}")
            hash = self.derive_file_hash(file.filename)
            visitor = ""
            try:
                visitor = self.list_smb_ips()
                visitor = visitor[0]
                logging.info(visitor)
            except Exception as e:
                logging.exception("Exception: {0}".format(e))
                visitor = "None"
            if hash is not None:
                entry = (datetime.now(), file.filename, hash, visitor)
                self.db.insert_data(*entry)
                self.encrypt_file(self.share_name, file.filename)

    def derive_file_hash(self, file_name: str) -> None:
        try:
            algo_obj = hashlib.sha256()
            with open("tempfile", "wb") as temp_file:
                self.connection.retrieveFile(self.share_name, file_name, temp_file)
            with open("tempfile", "rb") as temp_file:
                while chunk := temp_file.read(8192):
                    algo_obj.update(chunk)
            logging.info(algo_obj.hexdigest())
            os.remove("tempfile")
            return str(algo_obj.hexdigest())
        except Exception as e:
            logging.exception("Exception: {0}".format(e))
            return None
        
    def retrieve_file_from_share(self, share_name, file_name, local_path):
        try:
            with open(local_path, "wb") as local_file:
                self.connection.retrieveFile(share_name, file_name, local_file)
            logging.info(f"File '{file_name}' retrieved from share '{share_name}' and saved as '{local_path}'")
        except Exception as e:
            logging.exception(f"Exception while retrieving file from share: {e}")

    def delete_file_on_share(self, share_name, file_name):
        try:
            self.connection.deleteFiles(share_name, file_name)
            logging.info(f"Deleted file '{file_name}' from share '{share_name}'")
        except Exception as e:
            logging.exception(f"Exception while deleting file from share: {e}")

    def list_smb_ips(self) -> list:
        try:
            result = subprocess.run(['sudo', 'smbstatus', '-S'], capture_output=True, text=True)
            output = result.stdout
            logging.info(output)
            ips = re.findall(r'^\s*\S+\s+\d+\s+(\d+\.\d+\.\d+\.\d+)', output, re.MULTILINE)
            unique_ips = list(set(ips))
            logging.info(f"Extracted IP addresses: {unique_ips}")
            return unique_ips
        except Exception as e:
            logging.exception(f"Exception while listing SMB IPs: {e}")
            return ['None']

    def list_smb_sessions(self) -> None:
        result = subprocess.run(['sudo', 'smbstatus', '-S'], capture_output=True, text=True)
        output = result.stdout
        logging.info(output)
        sessions = re.findall(r'^\s*\S+\s+(\d+)\s+(\d+\.\d+\.\d+\.\d+)', output, re.MULTILINE)
        unique_sessions = [(pid, ip) for pid, ip in sessions]
        # logging.info(f"Extracted PID and IP pairs: {unique_sessions}")
        return unique_sessions

    def terminate_smb_sessions(self, sessions) -> None:
        if sessions:
            for pid, ip in sessions:
                logging.info(f"PID: {pid}, IP: {ip}")
                logging.info(f"Attempting to terminate SMB session with PID {pid}")
                # result = subprocess.run(['sudo', 'smbcontrol', 'smbd', 'close-share', f'pid={pid}'], capture_output=True, text=True)
                result = subprocess.run(['sudo', 'smbcontrol', 'smbd', 'close-share', self.share_name], capture_output=True, text=True)
                logging.info(f"smbcontrol output: {result.stdout}")
                logging.error(f"smbcontrol error: {result.stderr}")
                logging.info(f"Terminated SMB session with PID {pid}")

    def close_smb_share(self):
        try:
            result = subprocess.run(['sudo', 'smbcontrol', 'smbd', 'close-share', self.share_name], capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"Successfully closed SMB share: {self.share_name}")
            else:
                logging.error(f"Failed to close SMB share: {self.share_name}")
        except Exception as e:
            logging.exception("Exception closing SMB share: {0}".format(e))

    def encrypt_file(self, share_name, file_name) -> None:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        local_path = f"{file_name}_{timestamp}"
        self.retrieve_file_from_share(share_name, file_name, local_path)
        try:
            with open(local_path, 'rb') as file:
                data = file.read()
            cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.iv))
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            encrypted_filename = "/tmp/"+local_path+'.enc'
            with open(encrypted_filename, 'wb') as encrypted_file:
                encrypted_file.write(self.iv+encrypted_data)
            self.delete_file_on_share(share_name, file_name)
        except Exception as e:
            logging.exception(f"Exception during encryption: {e}")
        try:
            os.remove(local_path)
            logging.info(f"Removed: {local_path}")
        except Exception as e:
            logging.exception(f"Exception while removing file: {e}")
        logging.info(f"File '{file_name}' has been encrypted and saved as '{encrypted_filename}'")

    def run(self) -> None:
        try:
            self.connect()
            self.enumerate_share()
            self.list_smb_sessions()
            self.close_smb_share()
            self.db.list_entries()
            #self.db.truncate_table()
            self.db.close()
        except ConnectionRefusedError as e:
            logging.exception(f"Connection refused: {e}")
            pass

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()

