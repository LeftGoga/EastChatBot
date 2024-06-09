import logging

from warcio import ArchiveIterator
import icu
from bs4 import BeautifulSoup as BS

from yadisk import YaDisk


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('DataRead.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


test = YaDisk(cache=True, use_cached_list=True)
stream = test.get_file('ascii.jp-2016-12.warc.gz')

transliterator = icu.Transliterator.createInstance("NFKC", icu.UTransDirection.FORWARD)  # инициализация нормализатора

for i, record in enumerate(ArchiveIterator(stream)):  # цикл по отдельным статьям в архиве
    if record.rec_type == 'response':
        # uri = record.rec_headers.get_header('WARC-Target-URI')  # ссылка на оригинал
        ct = record.http_headers.get_header('Content-Type')
        # Тип контента, т.к. могут сохраняться изображения в этот файл, и все прочие
        date = record.http_headers.get_header('WARC-Date')  # дата сохранения страницы

        http_content = record.content_stream().read()
        if 'text/html' in ct:  # это html-ка
            html_content = ''  # дабы IDE не ругалась, на отсутствие переменной (переменная создаётся в одной ветки условия)
            status = record.http_headers.statusline  # статус скачанного
            if status == '200 OK':  # скачано нормально

                detector = icu.CharsetDetector()
                detector.setText(record.content_stream().read())
                result = detector.detect()
                encoding = result.getName()
                try:
                    html_content = http_content.decode(encoding)
                except UnicodeDecodeError as message:
                    for alt_encoding in ['utf-8', 'KOI8-R', 'Big5:', 'latin-1', 'windows-1251']:
                        try:
                            html_content = http_content.decode(alt_encoding)
                            break
                        except UnicodeDecodeError:
                            pass
                    else:
                        logger.info(message)

                html_soup = BS(html_content, features="lxml")
                title = html_soup.title.text  # выдираем название статьи
                body = html_soup.body  # отдираем содержимое тега body, остальное не нужно

                list_tags = ['script', 'footer', 'header']  # теги которые будут удалены вместе с содержимым
                for item in body.find_all(list_tags):  # поиск хлама
                    item.decompose()   # удаление хлама
                print(body.get_text())

                list_class = ['search']  # какие классы убиваем
                # find_all(string=re.compile('nav')
                # find('div', {"class": 'article-content'})
                for item in body.find_all('div', {'class': 'search'}):  # ищем
                    item.decompose()  # удаляем

                # цикл тупо записывает извлечённую хтмлку в директорию (мне нужны для анализа, что килять)
                # with open(f'cache\\html\\html_{i}.html', 'wb') as f:
                #     f.write(http_content)

                # цикл ниже падает, т.к. нет правильного указания как правильно интерпретировать выхлоп Супа
                # with open(f'cache\\html\\html_{i}_clean.html', 'w') as f:
                #     f.write(body.get_text().decoding(body.get_text()))

                # html = record.content_stream().read().decode()  # контент преобразуем в текст
                # clean_html = html2text.html2text(html_content)  # передаём html преобразователю в текст
