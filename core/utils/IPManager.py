import sqlite3
import csv
from core.constants import IP_DB_NAME
from core.utils.log import error

class IPManager:
    @staticmethod
    def initialize_db():
        conn = sqlite3.connect(IP_DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ip_addresses
                     (username TEXT PRIMARY KEY, ip_address TEXT UNIQUE)''')
        conn.commit()
        conn.close()

    @staticmethod
    def update_db_from_csv(csv_file_name):
        conn = sqlite3.connect(IP_DB_NAME)
        c = conn.cursor()
        with open(csv_file_name, newline='') as csvfile:
            ip_reader = csv.reader(csvfile, delimiter=',')
            for row in ip_reader:
                ip = row[0]
                try:
                    c.execute("INSERT OR IGNORE INTO ip_addresses (ip_address) VALUES (?)", (ip,))
                except sqlite3.IntegrityError:
                    print(f"IP address {ip} is already in use.")
        conn.commit()
        conn.close()
    
    @staticmethod
    def assign(username):
        conn = sqlite3.connect(IP_DB_NAME)
        c = conn.cursor()
        # Check if the user already has an assigned IP address
        c.execute("SELECT ip_address FROM ip_addresses WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            error(f"User '{username}' is already assigned an IP address.")
            return
        
        # Proceed with IP address assignment
        c.execute("SELECT ip_address FROM ip_addresses WHERE username IS NULL LIMIT 1")
        ip_row = c.fetchone()
        if ip_row:
            ip_address = ip_row[0]
            c.execute("UPDATE ip_addresses SET username = ? WHERE ip_address = ?", (username, ip_address))
            conn.commit()
        else:
            conn.close()
            raise ValueError("No IP addresses left to assign.")
        
        conn.close()
        return ip_address
    
    @staticmethod
    def get_ip(username):
        conn = sqlite3.connect(IP_DB_NAME)
        c = conn.cursor()
        c.execute("SELECT ip_address FROM ip_addresses WHERE username = ?", (username,))
        ip_row = c.fetchone()
        if ip_row:
            return ip_row[0]
        else:
            raise ValueError(f"No IP address found for username {username}")
        conn.close()

IPManager.initialize_db()