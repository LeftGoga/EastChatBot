import chromadb as cdb

import os.path

class DB_connector:
    """
    Класс для работы с ChromaDB

    """

    def __init__(self, path=os.getcwd()+"\DataBase"):
        """
        Создается база данных
        :param path: путь до бд
        """
        self.client= None
        self.path = path
        self.collectionList = []
        self.create_db(self.path)


    def create_db(self):

        """
        Класс созадния бд
        :return:
        """
        file = self.path+"\chroma.sqlite3"
        if not os.path.isfile(file):#чекаем если уже файл

            try:
                self.client = cdb.PersistentClient(self.path)
            except Exception as e:
                print(e)
        else:
            print("db already exists")

    def create_collection(self, collection_name):

        """
        Создание коллекции

        :param collection_name:
        :return:
        """

        try:
            coll = self.client.create_collection(collection_name)
            self.collectionList.append(coll)
        except Exception as e:
            print(e)
    def add_to_collection(self,collection_name,text,metadata, checking=True):

        """
        Добавление в коллекцию. Есть чек на дубли
        :param collection_name:
        :param text:
        :param metadata:
        :param checking:
        :return:
        """

        flag = True
        try:
            coll = self.client.get_collection(collection_name)
            check = coll.query([text])
            if checking:
                for i in check["distances"]:
                    if i <1:
                        print("дубликат")
                        flag = False
            if flag :
                coll.add([text],[metadata])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    db= DB_connector()
