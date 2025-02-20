import aiosqlite
import logging
from logging.handlers import RotatingFileHandler
from specs import specs

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(RotatingFileHandler(filename=f"{specs.logs_path}{__name__}.log",
                                      mode='w',
                                      maxBytes=1024 * 1024))


async def create_db(db_file: str = f'{specs.db_path}bot_database.db', tasks: bool = False,
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
            logger.info(msg='Succeed to create tasks db')
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
            logger.info(msg='Succeed to create users db')
        except Exception as e:
            logger.exception(msg=f'Failed to create users db: {e}')
    if links:
        try:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT,
                creator_id INT,
                time_weight REAL DEFAULT 3.0,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transition_count INT DEFAULT 0,
                weight REAL GENERATED ALWAYS AS (time_weight + transition_count * 0.8)
                
                );
                ''')
                await db.commit()
            logger.info(msg='Succeed to create links db')

            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS link_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER,
                transition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (link_id) REFERENCES links(id)
                );
                ''')
                await db.commit()
            logger.info(msg='Succeed to create links_transitions db')

            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TRIGGER IF NOT EXISTS update_transition_count
                AFTER INSERT ON link_transitions
                FOR EACH ROW
                BEGIN
                UPDATE links
                SET transition_count = (
                    SELECT COUNT(*)
                    FROM link_transitions
                    WHERE link_id = NEW.link_id
                      AND transition_time >= datetime('now', '-24 hours')
                )
                WHERE id = NEW.link_id;
                END;
                ''')
                await db.commit()
            logger.info(msg='Succeed to create update_transition_count db')

            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TRIGGER IF NOT EXISTS update_transition_count_after_delete
                AFTER DELETE ON link_transitions
                FOR EACH ROW
                BEGIN    
                UPDATE links
                SET transition_count = (
                SELECT COUNT(*)
                FROM link_transitions
                WHERE link_id = OLD.link_id
                AND transition_time >= datetime('now', '-24 hours')
                )
                WHERE id = OLD.link_id;
                END;
                ''')
                await db.commit()
            logger.info(msg='Succeed to create update_transition_count_after_delete db')


        except Exception as e:
            logger.exception(msg=f'Failed to create links or links_transitions db: {e}')


async def update_time_weight_links(db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                       UPDATE links
                       SET time_weight = CASE
                       WHEN (strftime('%s', 'now') - strftime('%s', creation_time) <= 12 * 3600 THEN 3
                       WHEN (strftime('%s', 'now') - strftime('%s', creation_time) <= 24 * 3600 THEN 2
                       WHEN (strftime('%s', 'now') - strftime('%s', creation_time) <= 48 * 3600 THEN 1
                       ELSE 0
                       END
                       ''')
            await db.commit()
        logger.info(msg='Succeed to update_time_weight_links db')
    except Exception as e:
        logger.exception(msg=f'Failed to update_time_weight_links db: {e}')


async def select_links(user_id: int, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute('''
            SELECT (link, weight) FROM links
            LEFT JOIN tasks
            ON links.link = tasks.link
            AND tasks.user_id = ?
            WHERE links.creator_id = ?
            AND tasks.link IS NULL;
            ''', (user_id, user_id)) as cursor:
                rows = await cursor.fetchall()
                logger.info(msg='Succeed to select_links db')
                return rows
    except Exception as e:
        logger.exception(msg=f'Failed to select_links db: {e}')


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
                          db_file: str = f'{specs.db_path}bot_database.db') -> int | list[int]:
    columns = {0: 'balance', 1: 'balance_hl'}
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute('''SELECT * FROM users WHERE user_id = ?''',
                                  (user_id)
                                  ) as cursor:
                row = await cursor.fetchone()
                if column == -1:
                    value = [row[columns.get(0)], row[columns.get(1)]]
                else:
                    value = row[columns.get(column)]
                logger.info(msg=f'Successed to update users db')
                return value
    except Exception as e:
        logger.exception(msg=f'Failed to update users db: {e}')


if __name__ == '__main__':
    pass
