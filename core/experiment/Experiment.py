import json
import os
import pickle as pkl
from core.utils.log import debug, error, info
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils import shuffleIP as IP
from core.utils.util import wait
from core.constants import BASE_DIR, getPlatform
from core.experiment.Subject import Subject
from trials.post import EXPERIMENT_ID

# make Experiment class singleton

class Experiment(): 
    _instance = None
    def __new__(cls, client_id, experiment_id):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_variables(client_id, experiment_id)
        return cls._instance
    
    def init_variables(self, client_id, experiment_id):
        self.client_id = client_id
        self.experiment_id = experiment_id
        self.config = open(self.config_path(), 'r')
        self.path = self.user_path()
        self.basicSetup()
    
    def screenshot_path(self):
        path = os.path.join(self.path, 'screenshots')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def log_file(self):
        file = os.path.join(self.path, 'log.txt')
        return file 

    def config_path(self):
        path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id, 'config.json')
        self.config = json.load(open(path, 'r'))
        return path
    
    def user_path(self):
        path = os.path.join(BASE_DIR, 'trials', 'data', self.client_id, 'data')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def basicSetup(self):
        items = ['google', 'youtube', 'reddit', 'twitter', 'facebook', 'youtube_pre', 'reddit_pre', 'twitter_pre', 'facebook_pre', 'youtube_treatment', 'reddit_treatment', 'twitter_treatment', 'facebook_treatment', 'youtube_post', 'reddit_post', 'twitter_post', 'facebook_post']
        if not os.path.exists(os.path.join(self.path, 'items.json')):
            items = {item: 0 for item in items}
            json.dump(items, open(os.path.join(self.path, 'items.json'), 'w'))

    def getItem(self, item):
        items = json.load(open(os.path.join(self.path, 'items.json'), 'r'))
        return items[f'{item}']

    def updateItem(self, item, value):
        items = json.load(open(os.path.join(self.path, 'items.json'), 'r'))
        items[f'{item}'] = value
        json.dump(items, open(os.path.join(self.path, 'items.json'), 'w'))
