import sys
import os
sys.path.append(os.path.join('Users', 'hussam', 'Desktop', 'Projects', 'algopologist')) # 317 win
sys.path.append('../../')
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
    CLIENT_ID = str(sys.argv[2])
    EXPERIMENT_ID = sys.argv[1]
    config_path = os.path.join(BASE_DIR, 'trials', 'data', EXPERIMENT_ID, 'config.json')
    config = json.load(open(config_path, 'r'))
    print(config['users'])

    email = config['users'][CLIENT_ID]['email']
    
    g = GoogleWorkspace()
    g.initiateUser(email)