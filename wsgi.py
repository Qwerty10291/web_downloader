from app import app
from dowloader import Downloader
from data.db_session import global_init

if __name__ == '__main__':
    global_init()
    downloader = Downloader()
    app.run()