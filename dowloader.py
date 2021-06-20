from typing import List
from data.db_session import create_session
import pandas as pd
import requests
from data import models
import json
from datetime import datetime
import time
import logging
import schedule
import threading

logging.basicConfig(filename='log.log', filemode='w')


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Downloader:
    def __init__(self) -> None:
        self.is_loading = False
        print('init')
        self.create_timer()

    def load_users(self) -> List[models.User]:
        self.session = create_session()
        users = self.session.query(models.User).all()
        return users

    def load_all(self):
        print('started at ', datetime.now().strftime('%H:%M'))
        self.is_loading = True
        errors = 0
        for user_data in self.load_users():
            if errors >= 5:
                time.sleep(180)
            self.session.expunge(user_data)
            user = User(user_data)
            if not user.start():
                errors += 1
        self.session.close()
        self.is_loading = False

    def create_timer(self):
        schedule.every().day.at('09:00').do(self.load_all)
        schedule.every().day.at('12:00').do(self.load_all)
        schedule.every().day.at('20:45').do(self.load_all)

        self.timer_thread = threading.Thread(
            target=self._schedule_cycle, daemon=True)
        self.timer_thread.start()

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.load_all, daemon=True)
        self.thread.start()

    def _schedule_cycle(self):
        while True:
            schedule.run_pending()
            time.sleep(60)


class User:
    def __init__(self, user: models.User) -> None:
        self.user = user
        self.db_session = create_session()
        self.db_session.add(user)
        self.main_link = 'https://my.lptracker.ru/login.php'
        self.login_link = 'https://my.lptracker.ru/rest/system/login'
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'})

        self.logger = logging.getLogger(user.login)

    def auth(self) -> bool:
        login = self.user.login
        password = self.user.password
        self.session.get(self.main_link)
        auth_status = self.session.post(self.login_link, data=json.dumps(
            {'email': login, 'password': password})).json()
        print(auth_status['status'])
        return auth_status['status'] == 1

    def set_status(self, status):
        for document in self.user.documents:
            document.state = status
        self.db_session.commit()

    def start(self):
        self.set_status('loading')
        if not self.auth():
            print('auth error ', self.user.login)
            self.logger.error('auth error')
            self.user.status == 'auth error'
            self.set_status('auth error')
            self.db_session.commit()
            self.session.close()
            return False

        for document in self.user.documents:
            if document.flag != 'true':
                continue
            try:
                print(document.link)
                data = self.session.get(document.link, timeout=10)
                print(data.status_code)
                if data.status_code != 200:
                    print('404 error', document.link)
                    self.logger.error('404 error: ' + document.link)
                    document.state = 'adress not found'
                    self.db_session.commit()
                    continue
                document.state = 'OK'
                document.update_date = datetime.now()
                pd.read_excel(data.content).to_csv(
                    f'documents/{document.id}.csv', encoding='utf-8', index=False)
                self.db_session.commit()
            except requests.exceptions.MissingSchema:
                document.state = 'invalid url'
                self.logger.error('invalid url: ' + document.link)
                self.db_session.commit()
                continue
        self.session.close()
        return True
