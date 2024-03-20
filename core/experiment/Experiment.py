import json
import os
import pickle as pkl
from utils.log import debug, error, info
from account_creation.GoogleWorkspace import GoogleWorkspace
from utils import shuffleIP as IP
from utils.util import wait
from constants import getPlatform
from experiment.Subject import Subject

class Experiment():
    def __init__(self, config, platform):
        self.init_variables()

        debug('Loading experiment config')
        self.config = json.load(open(config, 'r'))
        path = self.config['path']
        self.platform = platform
        self.experiment_file = os.path.join(path, rf'{self.platform}-experiment.pickle')

        if os.path.isfile(self.experiment_file):
            debug('Loading experiment')
            self.load_from_pickle()
        else:
            debug('Saving experiment')
            self.save()

    def init_variables(self):
        self.config = None
        self.initiated = False
        self.tick = None

    def load_from_pickle(self):
        with open(self.experiment_file, 'rb') as file:
            loaded_object = pkl.load(file)
            self.__dict__.update(loaded_object.__dict__)

    def save(self):
        path = self.config['path']
        experiment_file = os.path.join(path, f'{self.platform}-experiment.pickle')
        pkl.dump(self, open(experiment_file, 'wb'))

    def subjects_exists(self):
        return os.path.isfile(os.path.join(self.config['path'], self.platform, 'subjects.list'))

    def get_subjects(self):
        subject_names = open(os.path.join(self.config['path'], self.platform, 'subjects.list'), 'r').read().split(',')
        subjects = []
        for subject_name in subject_names:
            subject = Subject()
            file_name = os.path.join(self.config['path'], self.platform, subject_name)
            subject.load(file_name)
            subjects.append(subject)
        return subjects
    
    def create_subjects(self):
        replication = self.config['replication']
        subject_list = []
        subjects = []
        for treatment in self.config['treatments']:
            for replicate in range(replication):
                action = treatment['action']
                topic = treatment['topic']
                name = f'{action}_{topic}_{replicate}' 
                subject = Subject()
                subject.create(self.config['path'], self.platform, name, action, topic, replicate, self.config['experiment_id'])
                subject_list.append(subject.id)   
                subjects.append(subject)

        subject_list = ','.join(subject_list)
        open(os.path.join(self.config['path'], self.platform, 'subjects.list'), 'w').write(subject_list)
        return subjects

    def initiate(self):
        if self.initiated:
            debug(f'Experiment {self.platform} already initiated.')
            return
        debug(f"Initiating {self.platform} experiment...")

        if self.subjects_exists():
            debug('\t Loading subjects')
            subjects = self.get_subjects()
        else:
            debug('\t Creating subjects')
            subjects = self.create_subjects()

        for subject in subjects:
            if subject.chrome_assigned:
                debug(f'\t Chrome already assigned {subject.id}:{subject.chromeid}')
                continue
            else:
                subject.assignChrome()

        self.initiated = True
        self.tick = 0
        self.save()

    def incrementTick(self):
        self.tick += 1
        self.save()
        debug("****** Experiment tick incremented ******")

    def run(self):
        self.save()
        increment_tick = self.run_platform(self.platform)
        if increment_tick:
            self.incrementTick()

    def run_platform(self, platform):
        tick_increment = 0
        debug(f'Running for platform: {platform}')
        subjects = self.get_subjects()
        for subject in subjects:
            debug(f'\t\t Subject: {subject.id} • Subject Tick {subject.tick} • Exp Tick {self.tick}')
            if subject.tick > self.tick:
                debug(f'\t\t Subject already run for tick {subject.tick}')
                continue
            IP.shuffle()
            info(f'CHECKING IF SIGNED IN')

            if not subject.checkChromeSignin():
                debug(f'\t Chrome Signing in subject: {subject.id}')
                info(f'NOT SIGNED IN')
                subject.chromeSignIn()

            if not subject.checkSignin():
                debug(f'\t\t Platform Signing in subject: {subject.id}')
                subject.platformSignIn()

            input('WAITING')
            subject.observe(pre=True)
            wait(3)
            subject.treatment()
            wait(3)
            subject.observe(pre=False)
            subject.incrementTick()
            tick_increment += 1
        return tick_increment > 0