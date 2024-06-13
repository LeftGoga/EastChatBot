import chromadb as cdb
import traceback
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
        self.create_db()


    def create_db(self):

        """
        Класс созадния бд
        :return:
        """
        file = self.path+"\chroma.sqlite3"
        if not os.path.isfile(file):#чекаем если уже файл

            try:
                self.client = cdb.PersistentClient(self.path,settings=cdb.Settings(allow_reset=True))
            except Exception as e:
                print(e)
        else:
            print("db already exists")
            self.client = cdb.PersistentClient(self.path,settings=cdb.Settings(allow_reset=True))
    def reset_db(self):
        self.client.reset()

    def create_coll(self, coll_name):

        self.client.create_colletion(coll_name)

    def add_to_collection(self,collection_name,ids,text,metadata=None, checking=True, dup_dist=1):

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
            coll = self.client.get_or_create_collection(collection_name)
            print(self.client.list_collections())
            check = coll.query(query_texts=text, n_results = 1)
            print(check)
            if check["distances"][0]!=[]:
                if checking:
                    for i in check["distances"]:
                        if i[0] < dup_dist:
                            print("дубликат")
                            flag = False
                            break
            if flag:
                print("adding")
                coll.add(ids=ids,documents=text, metadatas = metadata)
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            # print("in add:", e)


    def query(self, q,coll_name,n_res=1):
        coll = self.client.get_collection(coll_name)
        results = coll.query(
            query_texts=q,  # Chroma will embed this for you
            n_results=n_res  # how many results to return
        )

        return results
    def list_collections(self):
        self.client.list_collections()

if __name__ == "__main__":
    db = DB_connector()
    db.reset_db()
    data=["some data", "different type of data"]
    metadatas = [{"source": "s1"}, {"source": "s2"}]

    db.add_to_collection("test_coll",data,metadatas)
    print(db.query(["some different data"],"test_coll"))
    db.add_to_collection("test_coll",data,metadatas)
    print(db.client.list_collections())
    print(db.query(coll_name ="test_coll",q="some data")["metadatas"][0][0])
