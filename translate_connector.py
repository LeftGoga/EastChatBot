import requests



class connector:
    def __init__(self, api_key, url):
        self.api_key=api_key
        self.url=url
        self.return_list=[]


    def make_requests(self,tran_list:list, lang_from:str="ru", lang_to = "ja"):
        """
        Сам реквест
        :param tran_list:
        :return: list of list
        """


        i=0
        length=len(tran_list)
        flag= False #нужен для одинчных запросов, поднимается когда последний кусок текста переведен
        while True:# идет пока не переведется весь текст

            temp_list = []

            while True:# идет пока не заполнится один запрос
                if length==1:
                    """
                    Кусок кода есть запрос на одичный перевод
                    """
                    if len(tran_list[0])<10_000: #лимит на длину запроса 10к

                        temp_list.append(tran_list[0])
                        flag = True
                        break

                    else:
                        """
                        Разбиение на батчи
                        """
                        temp_list.append(tran_list[0][:10_000])
                        tran_list[0]=tran_list[0][10_000:]
                        break

                else:
                    """
                    Код для запроса на перевод списка элементов
                    """
                    if len(tran_list[i])<10_000:

                        temp_list.append(tran_list[i])
                        if i+1<length:#тут я так и не понял, какого хрена надо делать две  отдельные проверки
                             if (len(tran_list[i])+len(tran_list[i+1])<10000):
                                i+=1 # Если к запросу еще можно добавить просто инкриментим счетчик->
                             else:
                                #-> иначе инкрементим и выходим
                                i+=1
                                break
                        else:
                            i+=1
                            break
                    else:
                        """
                        Обрезание слишком больших элементов
                        """
                        temp_list.append(tran_list[i][:10_000])
                        tran_list[i]=tran_list[i][10_000:]
                        break

            #сам запрос к API
            response = self.__call_api({"sourceLanguageCode": lang_from,"targetLanguageCode" : lang_to,"texts" : temp_list})['translations']

            #Добавление запроса в общий список
            self.return_list.append([x["text"] for x in response])
            if (i>=length) | (flag):
                #весь списко переведен
                break



        return self.return_list


    def __call_api(self, data:list):

        """
        Запрос к API транслейта
        :param data: Текст для переввода
        :return: json
        """

        headers = {"Authorization": f"Api-Key {self.api_key}"}
        return requests.post(self.url, json=data, headers=headers).json()


if __name__ == "__main__":
    con = connector('API',
                    "https://translate.api.cloud.yandex.net/translate/v2/translate")
    text = ["Что нибудь"]
    print(con.make_requests(text, 'ru', 'ja'))