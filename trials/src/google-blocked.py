import sys
import os

sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append('../../')
sys.path.append(os.path.join('H:/', 'Desktop', 'algopologist')) # 301 lab
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist')) # 317 win
from core.experiment.Experiment import Experiment

from core.constants import IP_DB_NAME, BASE_DIR
import json
from core.browser.Selenium import BrowserFactory
from core.account_creation.GoogleWorkspace import GoogleWorkspace

if __name__ == '__main__':
    BrowserFactory('uc_single')
    CLIENT_ID = str(sys.argv[2])
    EXPERIMENT_ID = sys.argv[1]
    Experiment(client_id='admin', experiment_id=EXPERIMENT_ID)
    config_path = os.path.join(BASE_DIR, 'trials', 'data', EXPERIMENT_ID, 'config.json')
    config = json.load(open(config_path, 'r'))
    print(config['users'])

    email = config['users'][CLIENT_ID]['email']
    
    g = GoogleWorkspace()
    g.initiateUser(email)