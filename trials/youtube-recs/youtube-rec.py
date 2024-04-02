import sys
import os
sys.path.append(os.path.join('C:/', 'Users', 'hussa', 'Desktop', 'algopologist'))

import json
from core.browser.Selenium import BrowserFactory
from core.account_creation.GoogleWorkspace import GoogleWorkspace
from core.utils.util import wait, bigWait
from core.utils.log import debug, error, logging

from core.users.User import User
from core.platforms.Youtube import Youtube

if __name__ == '__main__':
    BrowserFactory('uc_single')

    i = sys.argv[1]

    config = json.load(open('config.json', 'r'))

    email = f'xp0nba{i}@spartaaceap.com'
    password = 'hehehahahoho'

    group = config[f"{i}"]
    training = config[group]
    seeds = config['seeds']

    print(f"Training: {training}")
    print(f"Seeds: {seeds}")

    g = GoogleWorkspace()
    g.initiateUser(email)

    user = User(Youtube, f'xp0nba{i}', 'yt-recs')
    user.chromeSignUp()

    for video in training:
        user.platform.addToHistory(video)

    user.platform.pauseHistory()

    recommendations = dict()
    for seed in seeds:
        user.search(seed)
        recommendations[seed] = user.platform.getRecommendations()

    json.dump(recommendations, open(f'.\\data\\recommendations_{i}.json', 'w'))

    BrowserFactory().getBrowser('see').forceCloseDriver()