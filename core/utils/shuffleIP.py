import sqlite3 as sql
import subprocess as sp
import pandas as pd
import requests
from core.utils.util import wait
from core.utils.log import debug, info, error
import core.constants as constants
import subprocess
import re




def getCurrentIP():
    result = subprocess.check_output("ipconfig", encoding='utf-8')

    # Search for Ethernet 2 adapter section
    ethernet_pattern = re.compile(r"(Ethernet adapter Ethernet 2.*?)(?:\r\n\r\n|\Z)", re.DOTALL)
    ethernet_match = ethernet_pattern.search(result)
    
    if ethernet_match:
        ethernet2_section = ethernet_match.group(1)
        ethernet2_section = ethernet2_section.split('Ethernet adapter')[1]
        
        if "Autoconfiguration" in ethernet2_section:
            error("Autoconfiguration IPv4 address for Ethernet 2 found. Using default IP.")
            return '128.255.45.220'
        # Search for the IPv4 Address within the Ethernet 2 section

        ipv4_pattern = re.compile(r"IPv4 Address.*?:\s+(\d+\.\d+\.\d+\.\d+)")
        ipv4_match = ipv4_pattern.search(ethernet2_section)
        
        if ipv4_match:
            ip = ipv4_match.group(1)
            info(f'Current IP Address: {ip}')
            return ip
        else:
            error("IPv4 address for Ethernet 2 not found.")
            return '128.255.45.220'
    else:
        error("Ethernet 2 not found in ipconfig output.")
        return '128.255.45.220'

def saveCurrentIP():
    ip = getCurrentIP()
    with open(constants.CURRENT_IP_FILE, 'w') as f:
        f.write(ip)

def isRunning():
    out = sp.check_output(r'schtasks.exe /query /tn "shuffleIP"', shell=True)
    if "Ready" in str(out):
        return False
    elif "Running" in str(out):
        return True
    else:
        raise Exception("Unknown state of task")

def internetAccess():
    timeout = 1
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

def getNewIP():
    debug("Getting New IP")
    with open(constants.IP_FILE, 'w') as f:
        f.write('get-ip')

    task_name = "shuffleIP"
    command = ["schtasks", "/run", "/tn", task_name]
    sp.run(command)
    while isRunning():
        wait(2)
    wait(4)
    if not internetAccess():
        raise Exception("No internet access after shuffling IP")

def setIP(ip):
    debug(f"Setting New IP: : {ip}")
    saveCurrentIP()
    if ip == getCurrentIP():
        debug("IP already set")
        return   

    with open(constants.IP_FILE, 'w') as f:
        f.write(ip)

    task_name = "shuffleIP"
    command = ["schtasks", "/run", "/tn", task_name]
    sp.run(command)

    while isRunning():
        wait(2)
    wait(5)
    if not internetAccess():
        debug('No internet access...')
        getNewIP()

def getIP(userID):
    # create ip address table
    query = '''CREATE TABLE "ips" (
        "id"	INTEGER,
        "ip"	TEXT,
    )'''
    db = sql.connect(constants.DATABASE)
    ip = db.execute(f"SELECT ip FROM ips WHERE id='{userID}'")
    ips = ip.fetchone()
    if ips == None:
        ip = None
    else:
        ip = ips[0]
    db.close()
    return ip

def updateTable(userID, ip):
    db = sql.connect(constants.DATABASE)
    db.execute(f"UPDATE ips SET ip='{ip}' WHERE id='{userID}'")
    db.commit()
    db.close()
    # append ip to the takens.txt file
    with open(constants.TAKEN_IP_FILE, 'a') as f:
        f.write(ip + '\n')

def shuffle(subject_name=''):
    if subject_name == '':
        getNewIP()
    else:
        debug(f"Shuffling IP for {subject_name}")
        ip = getIP(subject_name)
        if ip == None:
            debug(f"No IP for {subject_name}.... Getting new IP")
            getNewIP()
        else:
            setIP(ip)
        
        # get current ip
        IP = getCurrentIP()
        debug(f"Current IP: {IP}")
        if IP == ip:
            debug(f"IP successfully set to {IP}")
        else:
            updateTable(subject_name, IP)