import re

class clear_html:
    def __init__(self,text):
        self.text=text

    def clear_pict(self):
        self.text = re.sub(r'\(.+\.png|\(.+\.jpg|\(.+\.jpeg\)',"",self.text)
    def clear_tabs(self):
        self.text = re.sub(r'\\n', "",self.text)
    def clear_spaces(self):
        self.text = re.sub(r'  ', "", self.text)


if __name__ == "__main__":
    test="[![    ](/ресурсы/firefox-6402e8f344.jpg)]\\n"
    print(test)
    clear = clear_html(test)
    clear.clear_pict()
    clear.clear_tabs()
    clear.clear_spaces()
    print(clear.text)