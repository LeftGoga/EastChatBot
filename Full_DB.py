import chromadb as db
from DB import db_connector
class full_db:
    def __init__(self):
        self.db= db_connector()
        for i in range(2016, 2024):
            self.db.client.create_collection(str(i))
        return self.db
