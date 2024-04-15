import sys
import os

from core.experiment.Experiment import Experiment
sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append('../')
sys.path.append(os.path.join('H:/', 'Desktop', 'algopologist')) # 301 lab
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist')) # 317 win

from core.constants import IP_DB_NAME, BASE_DIR
from core.utils.IPManager import IPManager
import json
from core.browser.Selenium import BrowserFactory
from core.utils.zookeeper import getId
from core.experiment.Subject import Subject
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils.util import wait, bigWait
from core.utils.log import debug, error, logging
from core.constants import PRAW



if __name__ == '__main__':
    BrowserFactory('uc_single')
    CLIENT_ID = "1"
    EXPERIMENT_ID = sys.argv[1]

    experiment = Experiment(CLIENT_ID, EXPERIMENT_ID)
    config = experiment.config
    
    experiment.basicSetup()

    platforms = config['platforms']
    experiment_id = config['experiment_id']
    topics = config['topics']

    email = config['users'][CLIENT_ID]['email']
    action = config['users'][CLIENT_ID]['action']
    topic = config['users'][CLIENT_ID]['topic']
    replicate = config['users'][CLIENT_ID]['replication']
    
    google_signed = experiment.getItem('google')
    if not google_signed:
        g = GoogleWorkspace()
        g.initiateUser(email)
        experiment.updateItem('google', 1)

    debug(f'Google signed in: {google_signed}')
    waiting = 3

    name = f'{action}_{topic}_{replicate}' 
    subjects = []
    for platform in platforms:
        subject = Subject()
        subject.create(platform, name, action, topic, replicate, experiment_id, email)
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
        signed_in = experiment.getItem(plt)
        if signed_in:
            debug(f'SIGNED IN: Platform: {subject.platform}, Subject: {subject.id}')
            continue

        debug(f'Platform: {subject.platform}, Subject: {subject.id}')
        try:
            signed = subject.platformSignIn()
            experiment.updateItem(plt, 1)
        except Exception as e:
            error(f'\t Error signing in {subject.id} on {subject.platform}')
            error(f'\t {e}')
        debug(f'Signed in {subject.id} on {subject.platform}')
        bigWait(waiting)

    debug("OBSERVING")

    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"{plt}_pre"
        observed = experiment.getItem(plt_obs)
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
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        bigWait(waiting)
        
    debug("TREATMENT")

    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"{plt}_treatment"
        treated = experiment.getItem(plt_obs)
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
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        bigWait(waiting)

    debug("OBSERVE")
    
    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"{plt}_post"
        observed = experiment.getItem(plt_obs)
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
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {platform}')
            error(e)
        bigWait(waiting)