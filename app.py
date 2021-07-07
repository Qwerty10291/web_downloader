from flask.json import jsonify
from dowloader import Downloader
from data.models import Document
from flask import Flask, render_template, send_file
from data.db_session import *
from flask_restful import Api
import api_resources

app = Flask(__name__)
api = Api(app)
api.add_resource(api_resources.StateResource, '/api/docs')
api.add_resource(api_resources.DocumentResource, '/api/docs/<int:doc_id>')
api.add_resource(api_resources.UserListResource, '/api/users')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/docs/<int:id>')
def document_download(id):
    session = create_session()
    document = session.query(Document).get(id)
    if not document:
        return 'Документа с таким id нет.'
    
    try:
        file = open(f'documents/{id}.csv', 'rb')
    except FileNotFoundError:
        return 'Документ еще не загружен'
    session.close()
    return send_file(file, as_attachment=True, mimetype='application/octet-stream',  attachment_filename=f'{document.name}.csv')

@app.route('/start')
def start():
    if downloader.is_loading:
        return {'error': 'Данные уже загружаются. Подождите окончания процесса'}
    downloader.run_in_thread()
    return {'success': 'OK'}

@app.route('/status')
def state():
    return jsonify({'status': downloader.is_loading})


if __name__ == '__main__':
    global_init()
    downloader = Downloader()
    app.run('0.0.0.0', port=8000, debug=False)