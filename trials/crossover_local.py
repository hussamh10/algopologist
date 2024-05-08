import sys
import os

sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append('../')
sys.path.append(os.path.join('H:/', 'Desktop', 'algopologist')) # 301 lab
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist')) # 317 win

from core.experiment.Experiment import Experiment
from core.constants import SMALL_WAIT_TIME, WAIT_TIME
from core.utils.IPManager import IPManager
import json
from core.browser.Selenium import BrowserFactory
from core.utils.zookeeper import getId
from core.experiment.Subject import Subject
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils.util import wait, waitMinute
from core.utils.log import clearLog, debug, error, logging
from core.constants import PRAW

def isGoogleSigned(experiment, email):
    google_signed = experiment.getItem('google')
    if not google_signed:
        g = GoogleWorkspace()
        g.initiateUser(email)
        experiment.updateItem('google', 1)
    debug(f'Google signed in: {google_signed}')

def setupSubjects(platforms, experiment_id, email, action, topic, replicate):
    name = f'{action}_{topic}_{replicate}' 
    subjects = []
    for platform in platforms:
        subject = Subject()
        subject.create(platform, name, action, topic, replicate, experiment_id, email)
        subjects.append(subject)

    chrome = subjects[0]
    return subjects,chrome

def isChromeSigned(chrome):
    signed = chrome.checkChromeSignin()
    debug(f'Chrome signed in: {signed}')
    if not signed:
        error(f'Chrome not signed in: {chrome.id}')
        chrome.chromeSignIn()

def signinPlatforms(experiment, subjects):
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
        waitMinute()

def observe(experiment, subjects, cross, dose):
    debug("OBSERVING")
    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"observations_{plt}_{dose}"
        observed = experiment.getItem(plt_obs)
        if observed:
            debug(f'ALREADY OBSERVED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)
        debug(f'OBSERVING: Platform: {subject.platform}, Subject: {subject.id}')

        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {plt}')
            error(f'Attempting to sign in {subject.id} on {plt}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {plt}')
                error(e)
                continue
        
        wait(3)
        try:
            subject.observe(dose)
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error observing {subject.id} on {plt}')
            error(e)
        waitMinute()

def noise(experiment, topics, actions, subjects, cross):
    debug("NOISE")

    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"noise_{plt}"
        treated = experiment.getItem(plt_obs)
        if treated:
            debug(f'ALREADY NOISED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)

        debug(f'NOISING: Platform: {subject.platform}, Subject: {subject.id}')
        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {plt}')
            error(f'Attempting to sign in {subject.id} on {plt}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {plt}')
                error(e)
                continue
            wait(3)

        try:
            subject.sendNoise(actions, topics)
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error noising {subject.id} on {plt}')
            error(e)
        waitMinute()

def treatment(experiment, topics, subjects, cross, dose):
    debug("TREATMENT")

    for subject in subjects:
        plt = subject.platform.lower()
        plt_obs = f"treatments_{plt}_{dose}"
        treated = experiment.getItem(plt_obs)
        if treated:
            debug(f'ALREADY TREATED: Platform: {subject.platform}, Subject: {subject.id}')
            continue
        wait(3)
        debug(f'TREATING: Platform: {subject.platform}, Subject: {subject.id}')
        if not subject.checkSignin():
            error(f'{subject.id} not signed in on {plt}')
            error(f'Attempting to sign in {subject.id} on {plt}')
            wait(3)
            try:
                subject.platformSignIn()
            except Exception as e:
                error(f'Error signing in {subject.id} on {plt}')
                error(e)
                continue
            wait(3)

        try:
            subject.treatment(topics)
            experiment.updateItem(plt_obs, 1)
        except Exception as e:
            error(f'Error treating {subject.id} on {plt}')
            error(e)
        waitMinute()

if __name__ == '__main__':
    clearLog()
    BrowserFactory('uc_single')
    EXPERIMENT_ID = sys.argv[1]
    CROSSOVER = sys.argv[2]
    CLIENT_ID = sys.argv[3]

    print(f'CLIENT_ID: {CLIENT_ID}, EXPERIMENT_ID: {EXPERIMENT_ID}, CROSSOVER: {CROSSOVER}')

    experiment = Experiment(CLIENT_ID, EXPERIMENT_ID, CROSSOVER)
    config = experiment.config
    
    experiment.basicSetup()

    platforms = config['platforms']
    experiment_id = config['experiment_id']

    email = config['users'][CLIENT_ID]['email']
    action = config['users'][CLIENT_ID]['action']
    replicate = config['users'][CLIENT_ID]['replication']

    topic = config['cross'][CROSSOVER]['topic']
    topics = config['topics'][topic]
    noise_topics = config['noise_topics'][CROSSOVER]
    noise_actions = config['noise_actions']
    dosage = config['dosage']
    
    isGoogleSigned(experiment, email)
    subjects, chrome = setupSubjects(platforms, experiment_id, email, action, topic, replicate)

    isChromeSigned(chrome)

    signinPlatforms(experiment, subjects)
    
    if int(CROSSOVER) > 0:
        observe(experiment, subjects, CROSSOVER, -1)

    noise(experiment, noise_topics, noise_actions, subjects, CROSSOVER)
    chrome.wait(1)
    observe(experiment, subjects, CROSSOVER, 0)

    for dose in range(dosage):
        chrome.wait(1)
        treatment(experiment, topics, subjects, CROSSOVER, dose)
        chrome.wait(1)
        observe(experiment, subjects, CROSSOVER, dose+1)

    try:
        os.system("killall -9 'Google Chrome'")
    except Exception as e:
        error(f'Error closing chrome: {e}')
