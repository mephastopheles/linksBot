from os import getenv as os_getenv
from os import makedirs as os_makedirs
from os import path as os_path


class Specs:
    def __init__(self, token: str, payment_token: str,
                 db_path: str = 'database/',
                 image_path: str = 'images/',
                 logs_path: str = 'logs/',
                 currency: str = 'RUB',
                 price=None,
                 price_hl=None,
                 ):
        if price_hl is None:
            price_hl = [10, 100]
        if price is None:
            price = [5000, 1000]
        self.token = token
        self.payment_token = payment_token

        self._db_path = db_path
        self._image_path = image_path
        self._logs_path = logs_path
        for path in [db_path, image_path, logs_path, 'excel/']:
            self.check_dirs(path)

        self.currency = currency
        self.price = price
        self.price_hl = price_hl
        self.choose_cost = {}

    @property
    def db_path(self):
        return self._db_path

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, new_path):
        self._image_path = new_path
        self.check_dirs(new_path)

    @db_path.setter
    def db_path(self, new_path):
        self._db_path = new_path
        self.check_dirs(new_path)

    @property
    def logs_path(self):
        return self._logs_path

    @logs_path.setter
    def logs_path(self, newp_path):
        self._logs_path = newp_path
        self.check_dirs(newp_path)

    @staticmethod
    def check_dirs(path: str = None):
        """Check and make directories"""
        if not os_path.exists(path):
            os_makedirs(path)


TOKEN = os_getenv('LINKS_BOT_TOKEN')
if TOKEN is None:
    TOKEN = '7808848463:AAGSecDwo25vqu-Y2VdR0AblCh-L8RHNJ6k'  # for test ONLY
    # TOKEN = '8022554679:AAG8aJIqmLhZsSCjARYlLR4RjdbPyXEd_Ac'  # for test ONLY

# PayMaster Test 2025-02-19 12:40
PAYMENT_PROVIDER_TOKEN = os_getenv('LINKS_BOT_PAYMENT_PROVIDER_TOKEN')
if PAYMENT_PROVIDER_TOKEN is None:
    PAYMENT_PROVIDER_TOKEN = "1744374395:TEST:6fa8118f24ba3436ace8"  # for test ONLY
    # PAYMENT_PROVIDER_TOKEN = "1744374395:TEST:bb3ad42501c03f0bfe62"  # for test ONLY

specs = Specs(token=TOKEN, payment_token=PAYMENT_PROVIDER_TOKEN)


class States:
    def __init__(self):
        self.START = 0
        self.SEND_LINK = 1
        self.ACCEPT_LINK = 2
        self.ACCOUNT = 3
        self.GET_LINK = 4


states = States()

if __name__ == '__main__':
    pass
