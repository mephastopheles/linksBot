import aiosqlite
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))

# Check directory exist
database_path = 'database/'
database_file = os.path.join(database_path, 'bot_links_database.db')

if not os.path.exists(database_path):
    os.makedirs(database_path)
    logger.info(f'Directory {database_path} successfully created')
else:
    logger.info(f'Directory {database_path} already exists')


async def create_tasks_db(db_file: str = 'database/bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute(f'''
            CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            link TEXT,
            photo_id TEXT
            )
            ''')
            await db.commit()
    except Exception as e:
        logger.exception(msg=f'Exception {e} raised')


async def insert_tasks_db(db_file: str = 'database/bot_database.db', username: str = '1',
                          link: str = '1', photo_id: str = '1'
                          ):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute(f'''
            INSERT INTO tasks (username, link, photo_id) VALUES (?, ?, ?);''',
                             (username, link, photo_id))
            await db.commit()

    except Exception as e:
        logger.exception(msg=f'Failed to insert tasks db, {e}')


#     db.execute('''CREATE TABLE IF NOT EXISTS users (
#     user_id INTEGER PRIMARY KEY,
#     username TEXT,
#     balance INTEGER DEFAULT 0
# )''')

if __name__ == '__main__':
    asyncio.run(create_tasks_db())
