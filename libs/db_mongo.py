from pymongo import MongoClient
from libs.db import Database
from libs.config import get_config


class MongoDatabase(Database):
    def __init__(self):
        pass

    def connect(self):
        config = get_config()

        self.client = MongoClient(config["db.dsn"])
        self.db = self.client[config["db.database"]]

    def insert(self, collection, document):
        # if not self.db:
        self.connect()

        return self.db[collection].insert_one(document).inserted_id
