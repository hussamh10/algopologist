import json
import sys
sys.path.append('C:\\Users\\hussa\\Desktop\\algopologist')

from core.browser.Selenium import BrowserFactory
from core.experiment.Experiment import Experiment
from core.utils.log import debug, error, logging
from core.utils.util import bigWait, wait
from ping import getItem, updateItem, basicSetup

def action(step, topics=None):
    subject_names = list(subjects.keys())
    for subject_name in subject_names:
        chrome = subjects[subject_name]['YouTube']
        signed = chrome.checkChromeSignin()
        debug(f'Chrome signed in: {signed}')
        if not signed:
            error(f'Chrome not signed in: {subject_name}')
            chrome.chromeSignIn()

        for platform in platforms:
            item = f'{step}_{platform}_{subject_name}'
            if getItem(item) == 1:
                debug(f'{subject_name} already {step}')
                continue
            print(f'Platform: {platform}, Subject: {subject_name}')
            subject = subjects[subject_name][platform]
            debug(f'Checking signin for {subject_name} on {platform}')
            wait(3)
            if not subject.checkSignin():
                error(f'{subject_name} not signed in on {platform}')
                error(f'Attempting to sign in {subject_name} on {platform}')
                wait(3)
                try:
                    subject.platformSignIn()
                except Exception as e:
                    error(f'Error signing in {subject_name} on {platform}')
                    error(e)
                    continue
                wait(3)

            try:
                debug(f'Performing {step} on {subject_name} on {platform}')
                if step == 'pre-observation':
                    subject.observe(pre=True)
                if step == 'treatment':
                    subject.treatment(topics)
                if step == 'post-observation':
                    subject.observe(pre=False)
                updateItem(item, 1)
            except Exception as e:
                error(f'Error {step} {subject_name} on {platform}')
                error(e)
        bigWait(5)


if __name__ == "__main__":
    BrowserFactory(browser_type='multi_ip')
    config = json.load(open('config.json', 'r'))
    platforms = config['platforms']
    topics = config['topics']
    print(config)

    experiment_subjects = dict()
    for platform in platforms:
        experiment = Experiment('config.json', platform)
        experiment.initiate()
        experiment_subjects[platform] = experiment.get_subjects()

    subjects = dict()
    for platform in platforms:
        for subject in experiment_subjects[platform]:
            if subject.id not in subjects:
                subjects[subject.id] = dict()
            subjects[subject.id][platform] = subject

    subject_names = list(subjects.keys())

    step = 'pre-observation'
    action(step)

    step = 'treatment'
    action(step, topics=topics)

    step = 'post-observation'
    action(step)
