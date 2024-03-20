import json
import sys
sys.path.append('C:\\Users\\hussa\\Desktop\\algopologist')

from core.utils.util import wait, bigWait
from core.utils.IPManager import IPManager
from core.utils.log import debug, error, logging

from core.experiment.Experiment import Experiment
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.browser.Selenium import BrowserFactory

if __name__ == "__main__":
    BrowserFactory(browser_type='multi_ip')
    config = json.load(open('config.json', 'r'))
    platforms = config['platforms']
    print(config)
    IPManager.initialize_db()
    # IPManager.update_db_from_csv('data\\ip.csv')

    GW = GoogleWorkspace()
    if GW.needUsers(config):
        debug("Creating users")
        GW.createUsers(config)

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
    print(subject_names)