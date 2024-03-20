import sys
import os
sys.path.append('C:\\Users\\hussa\\Desktop\\algopologist')

import sqlite3
import pandas as pd
from core.constants import IP_DB_NAME


ips = open("../res/webshare_proxies.txt", "r").read().split("\n")
user_ips = []

for ip in ips:
    ip = ip.split(":")
    user_ip = f'{ip[2]}:{ip[3]}@{ip[0]}:{ip[1]}'
    print(user_ip)
    user_ips.append(user_ip)

print(IP_DB_NAME)
conn = sqlite3.connect(IP_DB_NAME)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS ip_addresses
                (username TEXT, ip_address TEXT UNIQUE)''')
conn.commit()
conn.close()

pd = pd.DataFrame(user_ips, columns=["ip_address"])
pd['username'] = None
pd = pd[['username', 'ip_address']]
conn = sqlite3.connect(IP_DB_NAME)
pd.to_sql('ip_addresses', conn, if_exists='replace', index=False)
print(pd.head())