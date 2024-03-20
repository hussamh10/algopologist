from core.utils.log import debug
from core.utils.util import wait
from time import sleep
from core.users.User import User
from core.platforms.Reddit import Reddit

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

    def runExperiment(self):
        debug('User loaded')

        dump = 'No Treatment'
        if self.action == '':
            pass

        if self.action == 'search':
            self.user.search(self.topic)

        if self.action == 'comment':
            self.user.comment(self.topic, self.supplement)

        if self.action == 'open':
            dump = self.user.openPost(self.topic)

        if self.action == 'dislike':
            self.user.dislikePost(self.topic)

        if self.action == 'like':
            dump = self.user.likePost(self.topic)

        if self.action == 'join':
            self.user.joinCommunity(self.topic)

        if self.action == 'follow':
            self.user.followUser(self.topic)

        if self.action == 'vanilla':
            if self.platform.name == 'reddit':
                self.user.joinCommunity(self.topic) 
            else:
                self.user.followUser(self.topic)

        sleep(2)
        self.user.goHome()
        wait(3)
        return dump