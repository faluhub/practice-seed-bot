import json
from mysql import connector
from mysql.connector.abstracts import MySQLCursorAbstract
from PracticeSeedBot.secrets import Database

schemas = [
    "CREATE SCHEMA `practiceseedbot` DEFAULT CHARACTER SET utf8mb4"
]

tables = [
    "CREATE TABLE `practiceseedbot`.`uuids` (`id` BIGINT NOT NULL, `uuid` LONGTEXT NULL, PRIMARY KEY (`id`))",
    "CREATE TABLE `practiceseedbot`.`seeds` (`seed` VARCHAR(100) NOT NULL, `message_id` BIGINT NOT NULL, `author_id` BIGINT NOT NULL, `seed_notes` LONGTEXT NULL, `upvotes` JSON NULL, `downvotes` JSON NULL, PRIMARY KEY (`seed`), UNIQUE INDEX `seed_UNIQUE` (`seed` ASC) VISIBLE, UNIQUE INDEX `message_id_UNIQUE` (`message_id` ASC) VISIBLE)",
]

alters = []

class Result:
    def __init__(self, cursor: MySQLCursorAbstract):
        self._cur = cursor
        self.rows = cursor.rowcount
    
    @property
    def value(self):
        fetch = self._cur.fetchone()
        if not fetch == None and not fetch[0] == None:
            if type(fetch[0]) == dict or type(fetch[0]) == list or (type(fetch[0]) == str and str(fetch[0])[0] in "{}[]"):
                return json.loads(fetch[0])
            else: return fetch[0]
        else: return None
    
    @property
    def value_all_raw(self):
        fetch = self._cur.fetchall()
        if not fetch == None:
            ret = []
            for i in fetch: ret.append(i[0])
            return ret
        else: return None

    @property
    def value_all(self):
        fetch = self.value_all_raw
        if not fetch == None:
            ret = []
            for i in fetch:
                if not i in ret:
                    ret.append(i)
            return ret
        else: return None

def connect():
    try: return connector.connect(
        host=Database.HOST,
        port=Database.PORT,
        user=Database.USER,
        passwd=Database.PASSWORD,
        use_unicode=True
    )
    except Exception as e: quit(f"Couldn't connect to DB: {e}")

def cursor(db):
    try: return db.cursor(buffered=True)
    except Exception as e: quit(f"Couldn't connect to DB's cursor: {e}")

def create():
    db = connect()
    cur = cursor(db)

    print("Creating schemas...")
    for i in schemas:
        schema = i.split("`")[1]
        try: (cur.execute(i), db.commit(), print(f"  Created schema '{schema}'"))
        except Exception as e: print(f"  Error creating schema '{schema}': {e}")
    
    print("Creating tables...")
    for i in tables:
        table = i.split("`")[3]
        try: (cur.execute(i), db.commit(), print(f"  Created table '{table}'"))
        except Exception as e: print(f"  Error creating table '{table}': {e}")
    
    print("Altering tables...")
    for i in alters:
        table = i.split("`")[3]
        try: (cur.execute(i), db.commit(), print(f"  Altered table '{table}'"))
        except Exception as e: print(f"  Error altering table '{table}': {e}")
    
    cur.close()
    del cur

def select(q):
    db = connect()
    cur = cursor(db)

    cur.execute(q)
    return Result(cur)

def update(q):
    db = connect()
    cur = cursor(db)

    cur.execute(q)
    db.commit()
    cur.close()
    del cur

def delete(table, guildid):
    db = connect()
    cur = cursor(db)

    cur.execute(f"DELETE FROM `{table}` WHERE guildid = `{guildid}`")
    db.commit()
    cur.close()
    del cur
