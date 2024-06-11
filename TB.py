import telebot, time
from io import BytesIO
import os
from translate_connector import connector
from DB import DB_connector
from GPT_connector import GPT_connector

bot = telebot.TeleBot('<TG_Token>')
con = connector('<API_KEY>', "https://translate.api.cloud.yandex.net/translate/v2/translate")
db = DB_connector()

print(db.list_collections())
#retriever = db.as_retriever()

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message=='/start':
        bot.send_message(message.from_user.id, f"Yo!")
        return
    print('Translating')
    text_ru = con.make_requests(message.text, 'ru', 'ja')
    print('Extracting prompt')
    ans = db.query(text_ru, "test_coll")['documents'][0]
    print("ans")
    text_ans = con.make_requests(ans, 'ja', 'ru')
    print("texts_ans")
    gpt_connector = GPT_connector('<API_KEY>', text_ans, '<FOLDER_ID>')
    gpt_recon = gpt_connector.make_requests(message.text)
    print(gpt_recon)
    bot.send_message(message.from_user.id, gpt_recon)

    
bot.polling(non_stop=True, interval=2)
