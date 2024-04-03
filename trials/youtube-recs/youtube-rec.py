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

    id = f'inner{i}'
    email = f'{id}@spartaaceap.com'
    password = 'password'

    group = config[f"{i}"]
    training = config[group]
    seeds = config['seeds']

    print(f"Training: {training}")
    print(f"Seeds: {seeds}")

    # g = GoogleWorkspace()
    # g.initiateUser(email)

    user = User(Youtube, id, 'yt-recs')
    user.chromeSignUp()

    for video in training:
        user.platform.addToHistory(video)

    user.platform.pauseHistory()

    wait(30)

    user.platform = user.Platform(id)
    user.platform.loadBrowser()
    user.platform.loadWebsite()

    recommendations = dict()
    for seed in seeds:
        recommendations[seed] = user.platform.getRecommendations(seed)

    homePage = user.platform.getHomePage()
    homePage = user.platform.getPagePosts(20)

    home = []
    for post in homePage:
        home.append(post['id'])
    recommendations['home'] = home

    json.dump(recommendations, open(f'.\\data\\recommendations_{i}.json', 'w'))

    BrowserFactory().getBrowser('see').forceCloseDriver()