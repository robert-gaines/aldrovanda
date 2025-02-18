from src.monitor import Monitor
from src.db import Database
import logging
import time

def monitor_script():
    db = Database()
    db.create_table()
    retry_delay = 5  # Initial delay in seconds
    max_delay = 300  # Maximum delay in seconds (5 minutes)
    
    while True:
        try:
            monitor = Monitor()
            monitor.run()
            retry_delay = 5  # Reset delay after a successful run
            time.sleep(5)
        except ConnectionRefusedError as e:
            logging.exception(f"Connection refused: {e}")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff
        except Exception as e:
            logging.exception(f"Exception: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor_script()