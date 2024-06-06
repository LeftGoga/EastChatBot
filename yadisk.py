import requests
from dataclasses import dataclass
from urllib.parse import urlencode
from os.path import exists, isfile, join, abspath, dirname
from os import makedirs
from json import dumps, loads
from io import BytesIO

info_url = 'https://cloud-api.yandex.net/v1/disk/public/resources?'  # инфа о содержимом ссылки
public_path = 'https://disk.yandex.ru/d/P3n_jwRc83TWCg'  # Сюда публичную ссылку
# public_path = 'https://disk.yandex.ru/d/BKGdAxdTVuRnNA'  # Сюда публичную ссылку


@dataclass
class FileInfo:
    """Дата класс для хранения инфы о файлах. В словарях хранятся именно его экземпляры!"""
    path: str  # "path": "/ja/ascii.jp-2016-12.warc.gz",    - путь к файлу
    type: str  # "type": "file",                            - тип объекта
    name: str  # "name": "ascii.jp-2016-12.warc.gz",        - имя файла
    file: str  # "file": "https://downloader.disk",         - путь для скачивания


cache_dir = join(dirname(abspath(__file__)), 'cache')  # директория "кэша"
cached_list_name = join(cache_dir, 'list_all.json')  # закэшированная инфа о списке файлов, описание тут: https://yandex.ru/dev/disk-api/doc/ru/reference/meta
if not exists(cache_dir):
    makedirs(cache_dir)

# параметры запроса к ЯД
req_params = {
    'public_key': public_path,
    'path': '/ja',
    'limit': 1000,
    'fields': 'type,path,name,_embedded.items.path,_embedded.items.type,_embedded.items.file,_embedded.items.name'
}


class YaDisk:
    def __init__(self, cache=False, use_cached_list=False):
        self.files = {}  # словарь всех файлов
        self.dates = {}  # словарь дат, в каждой дате список файлов.
        self.cache = cache  # используем-ли кэш
        self.use_cached_list = use_cached_list  # загружать-ли файл с ЯД

        self.prepare_lists()  # подготовка к работе

    def __check_cache(self, filename):
        """ Проверяем есть-ли файл в кеше, и если есть, то вычитываем его и отдаём.
        Не трогаем"""
        full_filename = join(cache_dir, filename)
        if exists(full_filename):
            with open(full_filename, 'rb') as f:
                file_data = f.read()
            return file_data
        else:
            return None

    def get_file(self, filename):
        """Запрашиваем файл. Если есть в кэше берём оттуда, нет, то качаем с сервера.
        Отдаёт файлообразный объект с содержимым файла."""
        print('Getting file <%s>... '%filename, end='')
        file_info: FileInfo = self.files.get(filename, None)
        if not file_info:
            print('not exists!')
            return None

        if self.cache:  # проверили кэш, и если файл есть, отдаём его содержимое
            print('check cache... ', end='')
            file_data = self.__check_cache(file_info.name)
            if file_data:
                print(' return cached file!')
                return BytesIO(file_data)

        print('download...', end='')
        d_url = file_info.file  # откуда скачиваем
        download_response = requests.get(d_url)
        file_data = download_response.content

        if self.cache:
            with open(join(cache_dir, filename), 'wb') as f:
                f.write(file_data)

        print('ok!')
        return BytesIO(file_data)

    def __download_list(self):
        """ Тупо скачивает список с сервера.
        Не трогаем"""
        print('Downloading list...', end='')
        f_info_url = info_url + urlencode(req_params)  # собираем урл
        response = requests.get(f_info_url)
        r_json = response.json()
        self.r_json = r_json

        if self.cache:  # сохраняем на память
            with open(cached_list_name, 'wb') as f:  # сохраняем на память
                f.write(response.content)

        print('ok')
        return r_json

    def prepare_lists(self):
        """ Подготавливает словари информации файлов: по именам и по датам """
        print('Prepare lists')
        if self.cache and self.use_cached_list and exists(cached_list_name):
            with open(cached_list_name) as f:
                self.r_json = loads(f.read())
        else:
            self.__download_list()
        # self.__download_list()

        files = self.files
        dates = self.dates
        items = self.r_json['_embedded']['items']

        for item in items:
            file_info = FileInfo(item['path'], item['type'], item['name'], item['file'])
            files[file_info.name] = file_info

            date = file_info.name[-15:-8]  # отсчитываем от конца имени файла, так длины нужных частей постоянны
            dates.setdefault(date, []).append(file_info)
        return files


if __name__ == '__main__':
    # import random
    from warcio import ArchiveIterator
    import html2text

    test = YaDisk(cache=True, use_cached_list=True)
    stream = test.get_file('jp.sputniknews.com-2022-05.warc.gz')

    for i, record in enumerate(ArchiveIterator(stream)):  # цикл по отдельным статьям в архиве
        if record.rec_type == 'response':
            # uri = record.rec_headers.get_header('WARC-Target-URI')  # ссылка на оригинал
            ct = record.http_headers.get_header('Content-Type')
            # тип контента, т.к. могут сохранятся и
            # изображения в этот файл, и все прочие

            if 'text/html' in ct:  # это html-ка
                status = record.http_headers.statusline  # статус скачанного
                if status == '200 OK':  # скачано нормально
                    html = record.content_stream().read().decode()  # контент преобразуем в текст
                    clean_html = html2text.html2text(html)  # передаём html преобразователю в текст
                    print(clean_html)

    # keys = list(test.files.keys())
    # for _ in range(5):
    #     f = random.choice(keys)
    #     fa = test.get_file(f)
    #     for record in ArchiveIterator(fa):
    #         record.content_stream()
    #         print(record.rec_headers.get_header('WARC-Target-URI'))

