import sys
import os
sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append(os.path.join('H:/', 'Desktop', 'algopologist')) # 301 lab
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist')) # 317 win

from core.constants import IP_DB_NAME
from core.utils.IPManager import IPManager
import json
from core.browser.Selenium import BrowserFactory
from core.utils.zookeeper import getId
from core.experiment.Subject import Subject
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils.util import wait, bigWait
from core.utils.log import debug, error, logging
from core.constants import PRAW


def getItem(path, item):
    items = json.load(open(os.path.join(path, 'items.json'), 'r'))
    return items[f'{item}']

def updateItem(path, item, value):
    items = json.load(open(os.path.join(path, 'items.json'), 'r'))
    items[f'{item}'] = value
    json.dump(items, open(os.path.join(path, 'items.json'), 'w'))

def basicSetup(path):
    items = ['google', 'youtube', 'reddit', 'twitter', 'facebook', 'youtube_pre', 'reddit_pre', 'twitter_pre', 'facebook_pre', 'youtube_treatment', 'reddit_treatment', 'twitter_treatment', 'facebook_treatment', 'youtube_post', 'reddit_post', 'twitter_post', 'facebook_post']
    if not os.path.exists(os.path.join(path, 'items.json')):
        items = {item: 0 for item in items}
        json.dump(items, open(os.path.join(path, 'items.json'), 'w'))

if __name__ == '__main__':
    BrowserFactory('uc_single')
    CLIENT_ID = getId()
    config = json.load(open('config.json', 'r'))
    path = config['path']
    path = os.path.join(path, CLIENT_ID)
    if not os.path.exists(path):
        os.makedirs(path)

    print(PRAW)
    print(PRAW['client_id'])
    basicSetup(path)

    platforms = config['platforms']
    experiment_id = config['experiment_id']
    topics = config['topics']

    email = config['users'][CLIENT_ID]['email']
    action = config['users'][CLIENT_ID]['action']
    topic = config['users'][CLIENT_ID]['topic']
    replicate = config['users'][CLIENT_ID]['replication']
    
    google_signed = getItem(path, 'google')
    if not google_signed:
        g = GoogleWorkspace()
        g.initiateUser(email)
        updateItem(path, 'google', 1)

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
        signed_in = getItem(path, plt)
        if signed_in:
            debug(f'SIGNED IN: Platform: {subject.platform}, Subject: {subject.id}')
            continue

        debug(f'Platform: {subject.platform}, Subject: {subject.id}')
        try:
            signed = subject.platformSignIn()
            updateItem(path, plt, 1)
        except Exception as e:
            error(f'\t Error signing in {subject.id} on {subject.platform}')
            error(f'\t {e}')
        debug(f'Signed in {subject.id} on {subject.platform}')
        bigWait(waiting)

    debug("OBSERVING")

    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"{plt}_pre"
        observed = getItem(path, plt_obs)
        if observed:
            debug(f'ALREADY OBSERVED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)
        debug(f'OBSERVING: Platform: {subject.platform}, Subject: {subject.id}')

        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {platform}')
            error(f'Attempting to sign in {subject.id} on {platform}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {platform}')
                error(e)
                continue
        
        wait(3)
        try:
            subject.observe(pre=True)
            updateItem(path, plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        # bigWait(waiting)
        
    debug("TREATMENT")

    for subject in subjects:
        plt = subject.platform.lower()
        if plt == 'youtube':
            continue
        plt_obs = f"{plt}_treatment"
        treated = getItem(path, plt_obs)
        if treated:
            debug(f'ALREADY TREATED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)
        debug(f'TREATING: Platform: {subject.platform}, Subject: {subject.id}')
        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {platform}')
            error(f'Attempting to sign in {subject.id} on {platform}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {platform}')
                error(e)
                continue
            wait(3)

        try:
            subject.treatment(topics)
            updateItem(path, plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        bigWait(waiting)

    debug("OBSERVE")
    
    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"{plt}_post"
        observed = getItem(path, plt_obs)
        if observed:
            debug(f'ALREADY OBSERVED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)
        debug(f'OBSERVING: Platform: {subject.platform}, Subject: {subject.id}')
        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {platform}')
            error(f'Attempting to sign in {subject.id} on {platform}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {platform}')
                error(e)
                continue
            wait(3)
            
        try:
            subject.observe(pre=False)
            updateItem(path, plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        bigWait(waiting)