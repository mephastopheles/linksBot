from os import getenv as os_getenv
from os import makedirs as os_makedirs
from os import path as os_path

from aiohttp import ClientSession
from json import dumps as json_dumps


class Specs:
    def __init__(self, token: str, payment_token: str, wallet: str,
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
        self.wallet = wallet

        self._db_path = db_path
        self._image_path = image_path
        self._logs_path = logs_path
        for path in [db_path, image_path, logs_path, 'excel/']:
            self.check_dirs(path)

        self.currency = currency
        self.price = price
        self.price_hl = price_hl
        self.choose_cost = {}
        self.payment_payload = {}

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
    TOKEN = '7808848463:AAGSecDwo25vqu-Y2VdR0AblCh-L8RHNJ6k'  # my
    # TOKEN = '8022554679:AAG8aJIqmLhZsSCjARYlLR4RjdbPyXEd_Ac'  # client

# PayMaster Test 2025-02-19 12:40
PAYMENT_PROVIDER_TOKEN = os_getenv('LINKS_BOT_PAYMENT_PROVIDER_TOKEN')
if PAYMENT_PROVIDER_TOKEN is None:
    PAYMENT_PROVIDER_TOKEN = "1744374395:TEST:6fa8118f24ba3436ace8"  #
    # PAYMENT_PROVIDER_TOKEN = "3XTdDgvuDsoWPBwDxEKCcVz1yxbNfaB0E8AMxldFFyQ3aQGCQ95qGe5JvYOkkjAU"  # LAVA

WALLET = ''

specs = Specs(token=TOKEN, payment_token=PAYMENT_PROVIDER_TOKEN, wallet=WALLET)


class States:
    def __init__(self):
        self.START = 0
        self.SEND_LINK = 1
        self.ACCEPT_LINK = 2
        self.ACCOUNT = 3
        self.ACCOUNT_ADD_BALANCE = 30
        self.ACCOUNT_CONFIRM_ADD = 31
        self.GET_LINK = 4


states = States()


# async def checkout():
#     headers = {'Authorization': specs.payment_token}
#
#     for user_id, transaction_id in specs.payment_payload.values():
#         data = {'id': specs.payment_payload.get(user_id)}
#         async with ClientSession() as session:
#             async with session.post(url='https://api.lava.ru/invoice/info',
#                                     headers=headers,
#                                     data=json_dumps(data),
#                                     ) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     if data['status'] == 'success':
#                         await update.message.reply_text(
#                             text='Баланс успешно пополнен',
#                             reply_to_message_id=update.message.message_id,
#                             reply_markup=start_keyboard
#                         )



from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

scheduler = AsyncIOScheduler()
# scheduler.add_job()

if __name__ == '__main__':
    pass
