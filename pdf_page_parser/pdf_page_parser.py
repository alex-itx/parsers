"""
на сайте https://www.recordpower.co.uk/ есть ссылка по клику на каталог
https://www.recordpower.co.uk/flip/Winter2020/mobile/index.html
перейдя на страницу каталога мы видим имитацию реального журнала с красивым перевертыванием страниц
где каждая страница является файлом jpg и при перелистывание прогружаются новые две страницы
цель - спарсить все jpg файлы и засунуть их в один общий pdf файл
если открыть вкладку сеть и листать страницы, будут появляться гет запросы на новые jpg файлы
их и будем забирать и вставлять в pdf
на гет запросе файла есть url файла немного отличающегося от url самого каталога -
https://www.recordpower.co.uk/flip/Winter2020/files/mobile/1.jpg
на нашу удачу все файлы пронумерованы и соответствуют своему номеру страницы в журнале,
поэтому что-бы найти нужную нам страницу, достаточно изменить ее номере в url,
всего страниц в журнале 48
кстати при просмотре страницы каталога сайт принимал мои действия как режим просмотра (а-ля видео),
и при нажатие правой кнопкой мыши предлагались действия для управлением просмотром,
естественно вариации перейти в режим разработчика там не было,
поэтому вот горячие клавиши для перехода в режим разработчика, вкладки сеть -
Ctrl + Shift + i
"""

import requests, img2pdf, os
from bs4 import BeautifulSoup

"""
и так нам надо пробежаться по всем страницам
создадим функцию для работы
"""
def get_data():
    headers = {
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }

    """
    создадим список куда мы будем параллельно добавлять наши файлы что бы потом записать их в pdf
    """
    img_list = []
    for i in range(1, 49):
        url = f'https://www.recordpower.co.uk/flip/Winter2020/files/mobile/{i}.jpg'
        req = requests.get(url, headers=headers)
        res = req.content

        """
        создадим папку для хранения медиа файлов
        далее записываем файлы в jpg формате так же как и любой другой файл
        только режим записи двоичный "wb" потому что так записываются картинки
        """
        with open(f'media/{i}.jpg', 'wb') as f:
            f.write(res)
            img_list.append(f'media/{i}.jpg')
            print(f'файл {i} из 48 сохранен')

    """
    файлы сохранены осталось только запихнуть их в pdf
    существует множество библиотек для работы с pdf файлами
    для нашей задачи отлично подойдет библиотека img2pdf
    и ее метод convert() которая принимает список файлов jpg
    сам же файл pdf записывается так же как и остальные,
    формат записи так же как и для картинок "wb"
    """
    with open('result.pdf', 'wb') as f:
        """
        в запись файла мы и вставляем нашу функцию из img2pdf
        """
        f.write(img2pdf.convert(img_list))
        print('pdf файл готов')



"""
на всякий случай покажу как записать сохраненные файлы в pdf вне одной функции (а после нее)
код будет закоментирован
"""
# # создадим функцию которая будет считывает файлы из папки и сохраняет их в pdf
# def write_to_pdf():
#     # список файлов можно создать функцией listdir() из библиотеки os,
#     # но список будет несортированный, функция принимает имя директории
#     # img_list = os.listdir('media')
#     # что бы не заморачиваться с сортировкой, можно написать генератор списка
#     img_list = [f'media/{i}.jpg' for i in range(1, 49)]
#     # далее так-же как и до этого записываем список в pdf файл
#     with open('result.pdf', 'wb') as f:
#         f.write(img2pdf.convert(img_list))
#         print('pdf файл готов')


def main():
    get_data()
    # write_to_pdf()

if __name__ == '__main__':
    main()
