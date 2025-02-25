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
                    links: bool = False,):
    if tasks:
        try:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                task TEXT,
                photo_id TEXT,
                task_id INT
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
                balance_hl INT DEFAULT 0,
                task TEXT,
                task_id INT
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
                CREATE TABLE IF NOT EXISTS pays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pays_sum INT
                );
                ''')
                await db.commit()
            logger.info(msg='Succeed to create_pays db')

        except Exception as e:
            logger.exception(msg=f'Failed to create links or links_transitions or pays db: {e}')


async def create_triggers_db(db_file: str = f'{specs.db_path}bot_database.db'):
    try:
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
        logger.info(msg='Succeed to update_transition_count_after_delete')

        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_old_links
            AFTER INSERT ON links
            FOR EACH ROW
            BEGIN
            DELETE FROM links WHERE creation_time < datetime('now', '-48 hours');
            END
            ''')
            await db.commit()
        logger.info(msg='Succeed to create delete_old_links db')

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
    except Exception as e:
        logger.info(msg=f'Failed to create_triggers_db: {e}')


async def insert_pays(user_id: int, pays_sum: int, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                      INSERT INTO pays (user_id, pays_sum) VALUES (?);
                       ''', (user_id, pays_sum))
            await db.commit()
        logger.exception(msg=f'Succeed to insert_pays db')
    except Exception as e:
        logger.exception(msg=f'Failed to insert_pays db: {e}')


async def select_pays(user_id=int, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute('''
            SELECT COUNT(*), SUM(pays_sum) FROM pays WHERE user_id = ?;
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                logger.info(msg=f'Succeed to select_pays db')
                return row

    except Exception as e:
        logger.exception(msg=f'Failed to select_pays db: {e}')


async def update_time_weight_links(db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                       UPDATE links
                       SET time_weight = CASE time_weight
                       WHEN creation_time <= datetime('now', '-12 hours') THEN 3
                       WHEN creation_time <= datetime('now', '-24 hours') THEN 2
                       WHEN creation_time <= datetime('now', '-48 hours') THEN 1
                       ELSE 0
                       END
                       ''')
            await db.commit()
        logger.info(msg='Succeed to update_time_weight_links db')
    except Exception as e:
        logger.exception(msg=f'Failed to update_time_weight_links db: {e}')


async def select_tasks(user_id: int, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute('''
            SELECT links.link,  links.weight, links.id FROM links 
            LEFT JOIN tasks ON links.id == tasks.task_id WHERE tasks.user_id != ? AND links.creator_id != ?
            UNION SELECT links.link,  links.weight, links.id FROM links 
            LEFT JOIN tasks ON links.id == tasks.task_id WHERE tasks.task_id IS NULL AND links.creator_id != ?

            ''', (user_id, user_id, user_id)) as cursor:
                rows = await cursor.fetchall()
                logger.info(msg='Succeed to select_tasks db')
                return rows
    except Exception as e:
        logger.exception(msg=f'Failed to select_tasks db: {e}')


async def select_links(user_id: int, link: str = None, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        if link is None:
            async with aiosqlite.connect(db_file) as db:
                async with db.execute('''
                SELECT link FROM links WHERE creator_id = ?;
                ''', (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    logger.info(msg='Succeed to select_links_db1')
                    return rows
        else:
            async with aiosqlite.connect(db_file) as db:
                async with db.execute('''
                SELECT id FROM links WHERE link = ?;
                ''', (link,)) as cursor:
                    row = await cursor.fetchone()
                    logger.info(msg='Succeed to select_links db2')
                    return row
    except Exception as e:
        logger.exception(msg=f'Failed to select_links db: {e}')


async def insert_links_db(user_id: int, link: str, db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                        INSERT INTO links (creator_id, link) VALUES (?, ?);''',
                             (user_id, link))
            await db.commit()

        logger.info(msg=f'Succeed to insert links db')
    except Exception as e:
        logger.exception(msg=f'Failed to insert links db: {e}')


async def insert_tasks_db(user_id: int, task: str, photo_id: str,task_id:int, db_file: str = f'{specs.db_path}bot_database.db',
                          ):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
            INSERT INTO tasks (user_id, task, photo_id, task_id) VALUES (?, ?, ?, ?);''',
                             (user_id, task, photo_id,task_id))
            await db.commit()
        logger.info(msg=f'Succeed to insert tasks db')
    except Exception as e:
        logger.exception(msg=f'Failed to insert tasks db: {e}')


async def insert_link_transitions_db(link_id, db_file: str = f'{specs.db_path}bot_database.db',
                                     ):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
            INSERT INTO link_transitions (link_id) VALUES (?);''',
                             (link_id,))
            await db.commit()
        logger.info(msg=f'Succeed to insert_link_transitions_db')
    except Exception as e:
        logger.exception(msg=f'Failed to insert_link_transitions_db: {e}')


async def insert_users_db(user_id: int, balance: int = 0, balance_hl: int = 0,
                          db_file: str = 'database/bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            await db.execute('''
                        INSERT OR IGNORE INTO users (user_id, balance, balance_hl) VALUES (?, ?, ?);''',
                             (user_id, balance, balance_hl))
            await db.commit()
        logger.info(msg=f'Succeed to insert_users_db')
    except Exception as e:
        logger.exception(msg=f'Failed to insert users db: {e}')


async def update_users_db(user_id: int, balance: int = 0, balance_hl: int = 0, task: str = None, task_id: int =None,
                          db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        if task is None:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                            UPDATE users 
                            SET balance = balance + ?, balance_hl = balance_hl + ? 
                            WHERE user_id = ?;''',
                                 (balance, balance_hl, user_id))
                await db.commit()
        else:
            async with aiosqlite.connect(db_file) as db:
                await db.execute('''
                            UPDATE users 
                            SET balance = balance + ?, balance_hl = balance_hl + ?, task = ?, task_id = ?
                            WHERE user_id = ?;''',
                                 (balance, balance_hl, task, task_id,user_id))
                await db.commit()
        logger.info(msg=f'Succeed to update_users_db')
    except Exception as e:
        logger.exception(msg=f'Failed to update users db: {e}')


async def select_users_db(user_id: int, column: int,
                          db_file: str = f'{specs.db_path}bot_database.db'):
    try:
        async with aiosqlite.connect(db_file) as db:
            async with db.execute('''SELECT balance, balance_hl, task, task_id FROM users WHERE user_id = ?''',
                                  (user_id,)
                                  ) as cursor:
                row = await cursor.fetchone()

                if column == -1:
                    value = row
                else:
                    value = row[column]
                logger.info(msg=f'Succeed to select_users_db')
                return value
    except Exception as e:
        logger.exception(msg=f'Failed to select_users_db: {e}')


if __name__ == '__main__':
    pass
