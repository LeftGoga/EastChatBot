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
    def __init__(self,api_key, context,links, q, folder_id):

        api_key = api_key
        self.folder = folder_id

        self.gpt = YandexLLM(folder_id=folder_id, api_key=api_key, model=YandexGPTModel.Pro)
        template= f"""
        Ты - профессиональный востоковед. Твоя задача - прочитать приложенный текст новости с новостного сайта :
        {context}
        
        и
        ответить на заданный вопрос по теме стран востока, полагаясь только на текст прочитанной новости:{q}
        Прочитай текст новости ниже и напиши правильный ответ на заданный вопрос. 
        Ответ должен быть связанным, логичным и основывающися на приложенной статье. Ответ должен быть не длинным, не более
        10 строчек текста. На используемые факты в своему ответе добавляй ссылки на сайт в формате библиотечных ссылок из приведенного дальше списка: {links}
"""
        self.gpt.instruction_text = template

    def make_requests(self):

        res = self.gpt.invoke(self.gpt.instruction_text)

        return res


    def __call_api(self, req):

        res = self.gpt.invoke(req)
        return res



if __name__ == "__main__":


    folder = "FOLDER"
    API = "AAPI"
    req="В каком году стали ставить компьютеры"
    context = "компьютеры стали ставить в 2016 году"
    conn = GPT_connector(API,req, context, folder)

    print(conn.make_requests())
