import random
import requests
import os
from core.utils.log import debug, info, error, log
from core.utils.util import bigWait, wait
from core.constants import KEY_DIR

class juicy():
    GOOGLE = 1
    FACEBOOK = 12
    TWITTER = 4

    def __init__(self):
        # load key from file ./res/juicysms.key
        path = os.path.join(KEY_DIR, 'juicysms.key')
        self.key = open(path, 'r').read().strip()
        self.order_number = None
        self.phone_number = None
        self.code = None
        self.area = 'USA'

    def get_balance(self):
        request = f'https://juicysms.com/api/getbalance?key={self.key}'
        response = requests.get(request)
        debug(response.text)

    def get_number_from_order(self, order_number):
        request = f'https://juicysms.com/api/getnumber?key={self.key}&order={order_number}'
        response = requests.get(request)
        debug(response.text)
        return response.text

    def reuse_number(self):
        pass

    def get_code(self):
        debug("key: " + self.key)
        debug("order_number: " + self.order_number)
        request = f'https://juicysms.com/api/getsms?key={self.key}&orderId={self.order_number}'
        response = requests.get(request)
        debug(response.text)
        if 'ORDER_EXPIRED' in response.text:
            raise Exception("Order expired")

        if 'WAITING' in response.text:
            return -1

        self.code = response.text.split('_')[-1]
        if '-' in self.code:
            self.code = self.code.split('-')[1]
        self.code = self.code.split(' ')[0]
        debug(self.code)
        return self.code


    def skip_number(self):
        request = f'https://juicysms.com/api/skipnumber?key={self.key}&orderId={self.order_number}'
        debug(request)
        response = requests.get(request)
        debug(response.text)

    def get_number(self, service='Google'):
        if service.lower() == 'google':
            service_id = self.GOOGLE
        elif service.lower() == 'facebook':
            random_minutes = random.randint(5, 25)
            bigWait(random_minutes)
            service_id = self.FACEBOOK
        elif service.lower() == 'twitter':
            service_id = self.TWITTER
        else:
            raise Exception('Service not supported')
        output = self.get_phone_number(service_id=service_id)
        if output == 'already open':
            if service.lower() == 'facebook':
                return -1, -1

        while output == 'already open':
            debug('already open')
            self.skip_number()
            output = self.get_phone_number(service_id=service_id)
            wait(5)

        if output == 'no balance':
             raise Exception("No balance")

        if output == 'success':
            return self.area, self.phone_number

    def get_phone_number(self, service_id=GOOGLE):
        debug("Trying UK")
        self.area = 'UK'
        request = f'https://juicysms.com/api/makeorder?key={self.key}&serviceId={service_id}&country={self.area}'
        response = requests.get(request)
        debug(response.text)

        if response.text == 'NO_PHONE_AVAILABLE':
            debug("Trying US")
            request = f'https://juicysms.com/api/makeorder?key={self.key}&serviceId={service_id}&country={self.area}'
            response = requests.get(request)
            debug(response.text)

            if response.text == 'NO_PHONE_AVAILABLE':
                debug("Trying NL")
                self.area = 'NL'
                request = f'https://juicysms.com/api/makeorder?key={self.key}&serviceId={service_id}&country={self.area}'
                response = requests.get(request)
                debug(response.text)

                if response.text == 'NO_PHONE_AVAILABLE':
                        log("No phone number available")
                        raise Exception("No phone number available")
        
        if 'ORDER_ALREADY_OPEN_' in response.text:
            self.order_number = response.text.split('_')[-1]
            return 'already open'
        
        if 'NO_BALANCE' in response.text:
            return 'no balance'

        self.order_number = response.text.split('_')[2]
        self.phone_number = response.text.split('_')[-1]
        return 'success'