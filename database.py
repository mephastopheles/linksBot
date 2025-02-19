import aiosqlite
import logging
from logging.handlers import RotatingFileHandler
from specs import specs

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{specs.logs_path}{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def create_tasks_db(db_file: str = f'{specs.db_path}bot_database.db', tasks: bool = False,
                          users: bool = False,
                          links: bool = False):
    if tasks:
        try:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                link TEXT,
                photo_id TEXT
                );
                ''')
                await db.commit()
        except Exception as e:
            logger.exception(msg=f'Failed to create tasks db: {e}')
    if users:
        try:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                user_id INT PRIMARY KEY,
                balance INT DEFAULT 0,
                balance_hl INT DEFAULT 0
                );
                ''')
                await db.commit()
        except Exception as e:
            logger.exception(msg=f'Failed to create users db: {e}')
    if links:
        try:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS links (
                
                );
                ''')
                await db.commit()
        except Exception as e:
            logger.exception(msg=f'Failed to create links db: {e}')


async def insert_tasks_db(user_id: int, link: str, photo_id: str, db_file: str = f'{specs.db_path}bot_database.db',
                          ):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
            INSERT INTO tasks (user_id, link, photo_id) VALUES (?, ?, ?);''',
                             (user_id, link, photo_id))
            await db.commit()

    except Exception as e:
        logger.exception(msg=f'Failed to insert tasks db: {e}')


async def insert_users_db(user_id: int, balance: int = 0, balance_hl: int = 0,
                          db_file: str = 'database/bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                        INSERT OR IGNORE INTO users (user_id, balance, balance_hl) VALUES (?, ?, ?);''',
                             (user_id, balance, balance_hl))
            await db.commit()

    except Exception as e:
        logger.exception(msg=f'Failed to insert users db: {e}')


async def update_users_db(user_id: int, balance: int = 0, balance_hl: int = 0,
                          db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                        UPDATE users 
                        SET balance = balance + ?, balance_hl = balance_hl + ? 
                        WHERE user_id = ?;''',
                             (balance, balance_hl, user_id))
            await db.commit()

    except Exception as e:
        logger.exception(msg=f'Failed to update users db: {e}')


async def select_users_db(user_id: int, column: int,
                          db_file: str = f'{specs.db_path}bot_database.db'):
    columns = {0: 'balance', 1: 'balance_hl'}
    if column in columns.keys():
        column_name = columns.get(column)
    else:
        column_name = columns.get(0)
        logger.warning(msg=f'Trying get by wrong key in select users db')
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''SELECT ? FROM users WHERE user_id = ?''',
                             (column_name, user_id)
                             )
            await db.commit()
        logger.info(msg=f'Successed to update users db')
    except Exception as e:
        logger.exception(msg=f'Failed to update users db: {e}')


if __name__ == '__main__':
    pass
