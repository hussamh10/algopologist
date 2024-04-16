import inspect
from time import sleep, time
import pandas as pd
import sqlite3
from uuid import uuid4 as uid
import os
from core.constants import *
from core.experiment.Experiment import Experiment
from core.utils.util import wait; 
from core.utils.log import debug, info, error

class User:
    def __init__(self, platform, chromeId, experiment_id):
        self.Platform = platform
        self.userId = chromeId
        self.chromeId = chromeId
        self.experiment_id = experiment_id
        self.info = {'platform': self.Platform.__name__, 'id': self.chromeId}
        pass


    def _addSource(self, source):
        ouid = str(uid())[:8]
        source['description'] = source.get('description', '').replace("'", "")
        source['name'] = source.get('name', '').replace("'", "")
        source['url'] = source.get('url', '').replace("'", "")
        source['secondary_source'] = source.get('secondary_source', '').replace("'", "")
        source['uid'] = ouid
        source['type'] = 'source'

        return source

        # conn = sqlite3.connect(DATABASE)
        # c = conn.cursor()
        # debug("INSERT INTO sources VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ( ouid, source['id'], source['platform'], source['origin'], source['position'], source['type'], source['name'], source['secondary_source'], source['followers'], source['description'], source['engagement'], source['url']))
        # c.execute("INSERT INTO sources VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
        #     ouid, source['id'], source['platform'], source['origin'], source['position'], source['type'], source['name'], source['secondary_source'], source['followers'], source['description'], source['engagement'], source['url']
        # ))
        # conn.commit()
        # conn.close()

    def _addPost(self, obj):
        ouid = str(uid())[:8]
        obj['description'] = obj.get('description', '').replace("'", "")
        obj['description'] = obj.get('description', '').replace('"', "")
        obj['name'] = obj.get('name', '').replace("'", "")
        obj['name'] = obj.get('name', '').replace('"', "")
        obj['url'] = obj.get('url', '').replace("'", "")
        obj['source'] = obj.get('source', '').replace("'", "")
        obj['uid'] = ouid
        obj['type'] = 'post'

        return obj

        # conn = sqlite3.connect(DATABASE)
        # insert = f"INSERT INTO posts VALUES ('{ouid}', '{obj['id']}', '{obj['platform']}', '{obj['origin']}', '{obj['position']}', '{obj['type']}', '{obj['source']}', '{obj['secondary_source']}', '{obj['likes']}', '{obj['comments']}', '{obj['shares']}', '{obj['views']}', '{obj['created_at']}', '{obj['title']}', '{obj['description']}', '{obj['media']}', '{obj['url']}', '{obj['is_ad']}')"
        # c = conn.cursor()
        # c.execute(insert)
        # conn.commit()
        # conn.close()


    def addSignal(self, action, object, object_type, info=''):
        try:
            if object_type == 'source':
                obj = self._addSource(object)
            elif object_type == 'post':
                obj = self._addPost(object)
            else:
                obj = object
        except Exception as e:
            error(f'Error adding object: {e}')
            obj = ''

        signal_id = str(uid())[:8]

        signal = dict()
        signal['id'] = signal_id
        signal['action'] = action
        signal['object_id'] = obj
        signal['time'] = int(time())
        signal['user'] = self.chromeId
        signal['platform'] = self.Platform.__name__
        signal['info'] = info
        signal['experiment_id'] = self.experiment_id
        return signal

    def addSignal_deprecated(self, action, object, object_type, info=''):
        try:
            if object_type == 'source':
                object_uid = self._addSource(object)['uid']
            elif object_type == 'post':
                object_uid = self._addPost(object)['uid']
            else:
                object_uid = object
        except Exception as e:
            error(f'Error adding object: {e}')
            object_uid = ''

        signal_id = str(uid())[:8]
        screenshot = f'{action}-{signal_id}.png'
        print(SCREENSHOTS_PATH, self.experiment_id, self.chromeId, self.Platform.__name__, action, signal_id)
        path = os.path.join(SCREENSHOTS_PATH, self.experiment_id)
        if not os.path.exists(path):
            os.makedirs(path)
        platform_name = self.Platform.__name__
        screenshot = os.path.join(path, self.chromeId, platform_name, screenshot)

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO signals VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            signal_id, action, object_uid, screenshot, int(time()), self.chromeId, self.Platform.__name__, info, self.experiment_id 
        ))
        conn.commit()
        conn.close()
        debug('Signal added: %s' % action)

    def checkSignin(self):
        debug(f'SIGNING IN: {self.chromeId}')
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        is_signedin =  self.platform.loggedIn()
        return is_signedin

    def chromeSignIn(self):
        debug(f'SIGNING IN: {self.chromeId}')
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        wait(2)

    def chromeSignUp(self):
        self.platform = self.Platform(self.chromeId)
        self.platform.loadBrowser()
        self.platform.loadWebsite()
        wait(4)
        email = self.platform.chromeLogin()
        debug('Email: %s' % email)
        self.takeScreenshot()
        wait(7)
  
    def followUser(self, topic):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        debug('Term searched')
        user = self.platform.followUser()
        self.takeScreenshot()
        signal = self.addSignal('follow', user, 'source', info=f'searched-{topic}')
        return signal
        wait(3)

    def getOpenedPosts(self):
        conn = sqlite3.connect(DATABASE)
        signals = pd.read_sql_query("SELECT * FROM signals WHERE action = 'open' AND user = '%s'" % (self.info['id']), conn)
        posts = pd.read_sql_query("SELECT * FROM posts WHERE platform = '%s'" % (self.info['platform']), conn)
        df = pd.merge(signals, posts, left_on='object_id', right_on='id')
        conn.close()
        posts = list(df['post_id'])
        return posts

    def openPost(self, topic):
        info(f"Opeining post for {topic}")
        sleep(2)
        self.search(topic)
        opened_posts = self.getOpenedPosts()
        post, opened = self.platform.openPost(already_opened=opened_posts)
        self.takeScreenshot()
        signal = self.addSignal('open', post, 'post', info=f'searched-{topic}')
        debug(f"OPENED POST: {post['id']}")
        return signal

    def likePost(self, topic):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        info('Term searched: %s' % topic)
        post, opened = self.platform.likePost()

        if post == None:
            error('No post found to like')
            raise Exception('No post found to like')

        # for open in opened:
        #     self.takeScreenshot()
        #     self.addSignal('open', open, 'post', info=f'searched-{topic}')

        if post != None:
            signal = self.addSignal('like', post, 'post', info=f'searched-{topic}')

        return signal
  
    def joinCommunity(self, topic,):
        wait(2)
        self.goHome()
        wait(2)
        self.search(topic)
        debug('Term searched')
        community = self.platform.joinCommunity()
        self.takeScreenshot()
        signal = self.addSignal('join', community, 'source', info=f'searched-{topic}')
        return signal

    def getPosts(self, scrolls, posts_n=10):
        posts = []
        
        if self.platform.name == 'facebook':
            for i in range(scrolls):
                self.platform.scrollDown()
                wait(1)
            self.platform.scrollTop()
            posts = self.platform.getPagePosts(posts_n+5)
            return posts
        
        for i in range(scrolls):
            self.platform.scrollDown()
            posts += self.platform.getPagePosts(posts_n)
            sleep(2)
        return posts

    def recordHome(self, scrolls=5):
        self.goHome()
        sleep(2)
        posts = self.getPosts(scrolls)
        image_path = self.takeScreenshot()
        return posts, image_path

    def goHome(self):
        try:
            self.platform.getHomePage()
        except Exception as e:
            self.platform.loadWebsite()
        wait(3.2)

    def search(self, key):
        self.platform.searchTerm(key)
        wait(4)
        self.takeScreenshot()
        signal = self.addSignal('search', None, '', info=f'searched-{key}')
        return signal

    def control(self):
        self.goHome()
        wait(3)
        self.takeScreenshot()
        signal = self.addSignal('control', None, '', info='control')
        return signal

    def scrollDown(self, num=1):
        for i in range(num):
            self.platform.scrollDown()

    def takeScreenshot(self):
        uuid = str(uid())[:4]
        action = inspect.stack()[1].function
        screenshot_path = Experiment().screenshot_path()
        image_path = os.path.join(screenshot_path, self.platform.name, action, f'{uuid}.png')
        if not os.path.exists(os.path.dirname(image_path)):
            os.makedirs(os.path.dirname(image_path))
        self.platform.screenshot(image_path)
        return image_path

    def closeDriver(self):
        self.platform.closeDriver()