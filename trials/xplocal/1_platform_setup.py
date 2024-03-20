import json
from experiment.Experiment import Experiment
from utils.log import debug, error, logging
from utils.util import bigWait


if __name__ == "__main__":
    config = json.load(open('config.json', 'r'))
    platforms = config['platforms']
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
    for subject_name in subject_names[4:]:
        # chrome = subjects[subject_name]['YouTube']
        # signed = chrome.checkChromeSignin()
        # debug(f'Chrome signed in: {signed}')
        # if not signed:
        #     error(f'Chrome not signed in: {subject_name}')
        #     chrome.chromeSignIn()

        for platform in platforms:
            debug(f'Platform: {platform}, Subject: {subject_name}')
            subject = subjects[subject_name][platform]
            try:
                debug(f'\t Signing in {subject_name} on {platform}')
                signed = subject.platformSignIn()
            except Exception as e:
                error(f'\t Error signing in {subject_name} on {platform}')
                error(f'\t {e}')
            debug(f'Signed in {subject_name} on {platform}')
        bigWait(5)