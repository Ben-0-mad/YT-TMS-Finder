import sqlite3
from termcolor import colored
from libs.db import Database
from libs.config import get_config
from libs.utils import grouper


class SqliteDatabase(Database):
    TABLE_SONGS = "songs"
    TABLE_FINGERPRINTS = "fingerprints"

    def __init__(self):
        self.connect()

    def connect(self):
        config = get_config()

        self.conn = sqlite3.connect(config["db.file"])
        self.conn.text_factory = str

        self.cur = self.conn.cursor()

        print(colored("sqlite - connection opened", "white", attrs=["dark"]))

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print(
            colored(
                "sqlite - connection has been closed", "white", attrs=["dark"]
            )
        )

    def query(self, query, values=[]):
        self.cur.execute(query, values)

    def executeOne(self, query, values=[]):
        self.cur.execute(query, values)
        return self.cur.fetchone()

    def executeAll(self, query, values=[]):
        self.cur.execute(query, values)
        return self.cur.fetchall()

    def buildSelectQuery(self, table, params):
        conditions = []
        values = []

        for k, v in enumerate(params):
            key = v
            value = params[v]
            conditions.append("%s = ?" % key)
            values.append(value)

        conditions = " AND ".join(conditions)
        query = "SELECT * FROM %s WHERE %s" % (table, conditions)

        return {"query": query, "values": values}

    def findOne(self, table, params):
        select = self.buildSelectQuery(table, params)
        return self.executeOne(select["query"], select["values"])

    def findAll(self, table, params):
        select = self.buildSelectQuery(table, params)
        return self.executeAll(select["query"], select["values"])

    def insert(self, table, params):
        keys = ", ".join(params.keys())
        values = list(params.values())

        query = "INSERT INTO songs (%s) VALUES (?, ?)" % (keys)

        self.cur.execute(query, values)
        self.conn.commit()

        return self.cur.lastrowid

    def insertMany(self, table, columns, values, split_size=800):
        for split_values in grouper(values, split_size):
            query = "INSERT OR IGNORE INTO %s (%s) VALUES (?, ?, ?)" % (
                table,
                ", ".join(columns),
            )
            self.cur.executemany(query, split_values)

        self.conn.commit()

    def get_song_hashes_count(self, song_id):
        query = "SELECT count(*) FROM %s WHERE song_fk = %d" % (
            self.TABLE_FINGERPRINTS,
            song_id,
        )
        rows = self.executeOne(query)
        return int(rows[0])
    
    def create_checked_ids(self):
        query = '''CREATE TABLE IF NOT EXISTS checked_ids
             (id TEXT)'''
        
        self.cur.execute(query)
        self.conn.commit()
    
    def add_checked_id(self, watch_id):
        if not self.in_checked_ids(watch_id):
            query = f"INSERT INTO checked_ids VALUES ('{watch_id}');"
            self.cur.execute(query)
            self.conn.commit()
        
    def in_checked_ids(self, watch_id):
        res = self.cur.execute(f"SELECT 1 FROM checked_ids WHERE watch_id = '{watch_id}'")
        if res.fetchall() != []:
            return True
        else:
            return False
    
    '''
    def __exit__():
        try:
            self.conn.close()
        except error as e:
            print(e)
    '''
    
