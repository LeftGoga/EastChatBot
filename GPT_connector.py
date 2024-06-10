import bs4
from langchain_core.runnables import RunnablePassthrough
from yandex_chain import YandexLLM, YandexGPTModel
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
class GPT_connector:
    def __init__(self,api_key,retriever,folder_id):

        api_key = api_key
        self.folder = folder_id
        self.retriever = retriever
        self.gpt = YandexLLM(folder_id=folder_id, api_key=api_key, model=YandexGPTModel.Pro)
        template= """
        Ты - профессиональный востоковед. Твоя задача - прочитать приложенный текст новости с новостного сайта :
        {context}
        
        и
        ответить на заданный вопрос по теме стран востока, полагаясь только на текст прочитанной новости:{question}
        Прочитай текст новости ниже и напиши правильный ответ на заданный вопрос. 
        Ответ должен быть связанным, логичным и основывающися на приложенной статье. Ответ должен быть не длинным, не более
        10 строчек текста.
        """
        self.promt =  ChatPromptTemplate.from_template(template)

    def make_requests(self, req):
        length_re = len(req)
        if length_re>10_000:
            return print("слишком длинный вопрос")

        res = self.__call_api(req)

        return res


    def __call_api(self, req):

        rag_chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.promt
                | self.gpt
                | StrOutputParser()
        )
        res = rag_chain.invoke(req)
        return res



if __name__ == "__main__":
    loader = WebBaseLoader(
        web_paths=(["https://ascii.jp/elem/000/001/427/1427252/"])
    )


    pages = loader.load()
    embedding_function = SentenceTransformerEmbeddings(model_name="distiluse-base-multilingual-cased-v2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(pages)
    vectorstore = Chroma.from_documents(splits, embedding_function)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

    folder = "<FOLDER_ID>"
    API = "<API_KEY>"
    req="В каком году стали ставить компьютеры"
    conn = GPT_connector(API,retriever,folder)
    print(conn.make_requests(req))