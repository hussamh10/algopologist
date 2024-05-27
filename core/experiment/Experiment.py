import json
import os
import sqlite3
from core.constants import BASE_DIR
from core.utils.log import info

class Experiment(): 
    _instance = None
    def __new__(cls, client_id="", experiment_id="", crossover=0):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_variables(client_id, experiment_id, crossover)
        return cls._instance
    
    def init_variables(self, client_id, experiment_id, crossover):
        self.crossover = crossover
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
        path = os.path.join(BASE_DIR, 'trials', 'data', self.experiment_id, 'data', self.client_id, self.crossover)
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
        dosage = self.config['dosage']

        platforms = self.config['platforms']

        items = ['google']
        items += [f'{platform.lower()}' for platform in platforms]
        items += [f'noise_{p.lower()}' for p in platforms]
        for platform in platforms:
            items.append(f'observations_{platform.lower()}_{-1}')
        for platform in platforms:
            items.append(f'observations_{platform.lower()}_{0}')
        for dose in range(dosage):
            for platform in platforms:
                items.append(f'treatments_{platform.lower()}_{dose}')
            for platform in platforms:
                items.append(f'observations_{platform.lower()}_{dose+1}')

        if not os.path.exists(os.path.join(self.path, 'items.json')):
            items = {item: 0 for item in items}
            json.dump(items, open(os.path.join(self.path, 'items.json'), 'w'))

        if not os.path.exists(os.path.join(self.path, 'posts_opened.db')):
            conn = sqlite3.connect(os.path.join(self.path, 'posts_opened.db'))
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE posts (post_id STRING, platform TEXT)')
            conn.commit()
            conn.close()


    def getItem(self, item):
        info(f'··· GET ITEM: {item}')
        items = json.load(open(os.path.join(self.path, 'items.json'), 'r'))
        return items[f'{item}']

    def updateItem(self, item, value):
        info(f'··· UPDATE ITEM: {item}: {value}')
        items = json.load(open(os.path.join(self.path, 'items.json'), 'r'))
        items[f'{item}'] = value
        json.dump(items, open(os.path.join(self.path, 'items.json'), 'w'))