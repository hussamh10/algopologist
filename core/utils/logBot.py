from time import sleep
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

class chatBot:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(chatBot, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Prevents __init__ from re-running if instance already exists
            self.initialized = True
            options = uc.ChromeOptions()
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-infobars")
            path = './test'
            options.add_argument('--headless')
            self.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False)
            try:
                chat_url = self.getChatWindow()
            except Exception as e:
                print(e)
                self.driver.quit()
            sleep(1)
            self.driver.get(chat_url)

    def getChatWindow(self):
        self.driver.get('https://www.youtube.com/@hussamhabib')
        live = self.driver.find_elements('xpath', '//a[@id="thumbnail"]')[1]

        is_live = self.driver.find_elements('xpath', '//span[@aria-label="LIVE"]')
        if not is_live:
            raise Exception('Channel is not live')

        href = live.get_attribute('href')
        video_id = href.split('=')[-1]
        return f'https://www.youtube.com/live_chat?is_popout=1&v={video_id}'

    def sendMessage(self, message):
        chat = self.driver.find_element('xpath', '//div[@aria-label="Chat..."]')
        chat.send_keys(message)
        sleep(0.4)
        chat.send_keys(Keys.RETURN)

    def __del__(self):
        self.driver.quit()