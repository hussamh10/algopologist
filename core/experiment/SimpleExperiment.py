import json
import os
from core.constants import BASE_DIR

class SimpleExperiment(): 
    _instance = None
    def __new__(cls, client_id="", experiment_id=""):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_variables(client_id, experiment_id)
        return cls._instance
    
    def init_variables(self, client_id, experiment_id):
        self.client_id = client_id
        self.experiment_id = experiment_id
        self.path = self.user_path()
        self.config = json.load(open(self.config_path(), 'r'))
        self.basicSetup()
    
    def screenshot_path(self):
        path = os.path.join(self.path, 'screenshots')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def log_file(self):
        file = os.path.join(self.path, 'log.txt')
        return file 

    def experiment_path(self):
        path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id)
        return path

    def config_path(self):
        path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id, 'config.json')
        return path
    
    def user_path(self):
        if self.client_id == 'admin':
            path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id)
            return path
        path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id, self.client_id, 'data')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def flatten(self, foo):
        for x in foo:
            if hasattr(x, '__iter__') and not isinstance(x, str):
                for y in self.flatten(x):
                    yield y
            else:
                yield x
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