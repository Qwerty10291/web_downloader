import requests
import json
import os
import sys


def p_exit():
    print('Нажмите enter для выхода из программы')
    input()
    sys.exit()


main_link = 'https://my.lptracker.ru/login.php'
login_link = 'https://my.lptracker.ru/rest/system/login'

login_data = {'email': input('введите логин:'),
              'password': input('введите пароль:')}


session = requests.Session()
session.headers.update(
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'})
session.get(main_link)
auth_status = session.post(login_link, data=json.dumps(login_data)).json()
if auth_status['status'] != 1:
    print(f'Ошибка авторизации - {auth_status["errors"]["message"]}')
    print('Проверьте данные для входа и повторите попытку')
    p_exit()


try:
    links = map(lambda x: x.replace('\n', ''), open(
        input('введите название файла с ссылками:'), 'r').readlines())
except FileNotFoundError:
    print('файл не найден. Проверьте название и попробуйте еще раз')
    p_exit()

directory = input(
    'введите имя папки с загружаемыми файлами(ничего, если в текущей):')
if directory:
    try:
        os.mkdir(directory)
        os.chdir(directory)
    except FileExistsError:
        os.chdir(directory)
    except:
        print('директория не найдена. Загружаю в текущую...')


for link in links:
    data = session.get(link)
    if data.status_code != 200:
        print(f'Ошибка загрузки - {link}')
        continue
    filename = data.headers.get(
        'Content-Disposition').split('; ')[1].split('=')[1]
    with open(filename, 'wb') as file:
        file.write(data.content)
    print(f'{link} - OK')
p_exit()