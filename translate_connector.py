import requests



class connector:
    def __init__(self, api_key, url, tran_list):
        self.api_key=api_key
        self.url=url
        self.tran_list = tran_list
        self.return_list=[]

    def make_requests(self):
        i=0
        length = len(self.tran_list)

        while True:


            temp_list = []

            while True:
                print("i: ",i)
                temp_list.append(self.tran_list[i])
                if (i+1<length) & (len(self.tran_list[i])+len(self.tran_list[i+1])<10000):
                    i+=1
                else:
                    print("break")
                    i+=1
                    break

            print(sum(map(len,temp_list)))
            response = self.call_api({"sourceLanguageCode": "ja","targetLanguageCode" : "ru","texts" : temp_list})['translations']
            print(response)
            if i+1==length:
                break

            #self.return_list.append([x["text"] for x in response])


        return self.return_list


    def call_api(self, data):
        headers = {"Authorization": f"Api-Key {self.api_key}"}
        return requests.post(self.url, json=data, headers=headers).json()
