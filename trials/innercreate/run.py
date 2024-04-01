import sys
import os
# sys.path.append("H:\\Desktop\\algopologist")
# sys.path.append(os.path.join('H:/', 'Desktop', 'spartaaceap', 'engine', 'src'))
# sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'Platform behavior' ))
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist'))

from core.constants import IP_DB_NAME, BASE_DIR, BASIC_PASSWORD
from core.utils.IPManager import IPManager
import json
from core.browser.Selenium import BrowserFactory
from core.utils.zookeeper import getId
from core.experiment.Subject import Subject
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils.util import wait, bigWait
from core.utils.log import debug, error, logging

def getItem(path, item):
    items = json.load(open(os.path.join(path, 'items.json'), 'r'))
    return items[f'{item}']

def updateItem(path, item, value):
    items = json.load(open(os.path.join(path, 'items.json'), 'r'))
    items[f'{item}'] = value
    json.dump(items, open(os.path.join(path, 'items.json'), 'w'))

def basicSetup(path):
    items = []
    for i in range(0, 20):
        items.append(f'google_{i}')
        items.append(f'youtube_{i}')
    if not os.path.exists(os.path.join(path, 'items.json')):
        items = {item: 0 for item in items}
        json.dump(items, open(os.path.join(path, 'items.json'), 'w'))

if __name__ == '__main__':
    BrowserFactory('uc_single')
    BASIC_PASSWORD = 'password'
    # for i in range(0, 20):

    CLIENT_ID = sys.argv[1]
    config = json.load(open('config.json', 'r'))

    path = os.path.join(BASE_DIR, 'trials', config['experiment_id'], 'data')
    if not os.path.exists(path):
        os.makedirs(path)

    basicSetup(path)

    platforms = config['platforms']
    experiment_id = config['experiment_id']
    topics = config['topics']

    email = config['users'][CLIENT_ID]['email']
    action = config['users'][CLIENT_ID]['action']
    topic = config['users'][CLIENT_ID]['topic']
    replicate = config['users'][CLIENT_ID]['replication']
    
    google_signed = getItem(path, f'google_{CLIENT_ID}')
    if not google_signed:
        g = GoogleWorkspace()
        g.initiateUser(email)
        updateItem(path, f'google_{CLIENT_ID}', 1)

    debug(f'Google signed in: {google_signed}')
    waiting = int(CLIENT_ID)

    name = f'{action}_{topic}_{replicate}' 
    subjects = []
    for platform in platforms:
        subject = Subject()
        subject.create(path, platform, name, action, topic, replicate, experiment_id, email)
        subjects.append(subject)

    chrome = subjects[0]

    signed = chrome.checkChromeSignin()
    debug(f'Chrome signed in: {signed}')
    if not signed:
        error(f'Chrome not signed in: {chrome.id}')
        chrome.chromeSignIn()


    debug("SIGNIN")

    for subject in subjects:
        plt = subject.platform.lower()
        signed_in = getItem(path, f'youtube_{CLIENT_ID}')
        if signed_in:
            debug(f'SIGNED IN: Platform: {subject.platform}, Subject: {subject.id}')
            continue

        debug(f'Platform: {subject.platform}, Subject: {subject.id}')
        try:
            signed = subject.platformSignIn()
            updateItem(path, f'youtube_{CLIENT_ID}', 1)
        except Exception as e:
            error(f'\t Error signing in {subject.id} on {subject.platform}')
            error(f'\t {e}')
        debug(f'Signed in {subject.id} on {subject.platform}')
        bigWait(2)
    
    BrowserFactory().getBrowser('').forceCloseDriver()