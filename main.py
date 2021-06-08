from pandas.core.frame import DataFrame
import requests
import json
import sys
import pandas as pd

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

doc:DataFrame = pd.read_excel(session.get(input()).content)
with open('out.csv', 'w') as file:
    file.write(doc.to_csv('main.csv', encoding='utf-8', index=False))