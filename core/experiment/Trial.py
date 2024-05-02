import pandas as pd
from core.utils.log import debug, error
from core.utils.util import bigWait, wait
from time import sleep
from core.users.User import User
from core.platforms.Reddit import Reddit
from core.constants import WAIT_TIME

class Trial():
    def __init__(self, action, topic, userid, platform, experiment_id):
        self.action = action
        self.topic = topic
        self.userid = userid
        self.platform = platform
        self.experiment_id = experiment_id

    def signUpUser(self):
        self.user = User(self.platform, self.userid, self.experiment_id)
        self.user.chromeSignUp()
        wait(4)

    def loadUser(self):
        self.user = User(self.platform, self.userid, self.experiment_id)
        self.user.chromeSignIn()

    def checkSignin(self):
        self.user = User(self.platform, self.userid, self.experiment_id)
        return self.user.checkSignin()

    def observe(self):
        dump, screenshot = self.user.recordHome(scrolls=6)
        return dump, screenshot

    def closeDriver(self):
        self.user.closeDriver()

    def makeNoise(self, actions, topics):
        debug('User loaded')
        signals = dict()

        for action in actions:
            try:
                searchable = topics[self.platform.name][action]
                if action == 'search':
                    debug(f'Searching: {searchable}')
                    signals[action] = self.user.search(searchable)

                if action == 'open':
                    debug(f'Opening: {searchable}')
                    signals[action] = self.user.openPost(searchable)

                if action == 'like':
                    debug(f'Liking: {searchable}')
                    signals[action] = self.user.likePost(searchable)

                if action == 'join':
                    debug(f'Joining: {searchable}')
                    signals[action] = self.user.joinCommunity(searchable)

                if action == 'follow':
                    debug(f'Following: {searchable}')
                    signals[action] = self.user.followUser(searchable)
            except Exception as e:
                error(e)

            sleep(2)
            self.user.goHome()
            bigWait(WAIT_TIME)

        return signals



    def runExperiment(self, topics, dose):
        #TODO: Add dose to the experiment
        debug('User loaded')
        searchable = topics[self.platform.name][self.action]
        debug(f'Searchable: {searchable}')

        signal = dict()
        if self.action == '':
            signal = self.user.control()
            pass

        if self.action == 'search':
            signal = self.user.search(searchable)

        if self.action == 'open':
            signal = self.user.openPost(searchable)

        if self.action == 'dislike':
            self.user.dislikePost(searchable)

        if self.action == 'like':
            signal = self.user.likePost(searchable)

        if self.action == 'join':
            signal = self.user.joinCommunity(searchable)

        if self.action == 'follow':
            signal = self.user.followUser(searchable)

        sleep(2)
        self.user.goHome()
        wait(3)
        return signal