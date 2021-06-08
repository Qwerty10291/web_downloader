from flask_restful import reqparse, Resource, request
from flask import jsonify
from data.db_session import create_session
from data.models import *

document_parser = reqparse.RequestParser()
document_parser.add_argument('login', required=True, type=str, location='form')
document_parser.add_argument(
    'password', required=True, type=str, location='form')
document_parser.add_argument('name', required=True, type=str, location='form')
document_parser.add_argument('link', required=True, location='form')
document_parser.add_argument('flag', default='false', location='form')


class StateResource(Resource):
    def get(self):
        session = create_session()
        documents = sorted(session.query(Document).all(), key=lambda x: x.id, reverse=True)
        data = jsonify([document.to_dict(only=('id', 'name', 'link', 'state', 'flag', 'update_date', 'user.login', 'user.password'))
                        for document in documents])
        return data

    def post(self):
        args = document_parser.parse_args()
        if not all([args.login, args.password, args.name, args.link, args.flag]):
            return jsonify({'error': 'все поля должны быть заполнены'})
        session = create_session()
        user = session.query(User).filter(User.login == args['login']).first()
        if not user:
            print(session.query(User).all())
            user = User(login=args['login'], password=args['password'])
            session.add(user)
            session.commit()
            print('new user')
            print(session.query(User).all())
        else:
            user.password = args['password']
        document = Document()
        document.name = args['name']
        document.link = args['link']
        document.flag = args['flag']
        document.user = user
        session.add(document)
        session.commit()
        return jsonify({'success': 'OK', 'id': document.id})



class DocumentResource(Resource):
    def get(self, doc_id):
        session = create_session()
        document = session.query(Document).get(doc_id)
        if not document:
            return jsonify({'error': 'записи с таким id нет'})
        return jsonify(document.to_dict(only=('id', 'name', 'link', 'state', 'flag', 'update_date', 'user.login', 'user.password')))

    def put(self, doc_id):
        args = request.json
        session = create_session()
        document = session.query(Document).get(doc_id)
        if not document:
            return jsonify({'error': 'записи с таким id не существует'})
        doc_user: User = document.user
        if args['login'] != doc_user.login:
            if len(doc_user.documents) < 2:
                print('delete user', doc_user.login)
                session.delete(doc_user)
                session.commit()
        user = session.query(User).filter(User.login == args['login']).first()
        if not user:
            user = User(login=args['login'], password=args['password'])
            session.add(user)
            session.commit()
        else:
            if user.password != args['password']:
                user.password = args['password']
        document.user = user
        document.name = args['name']
        document.link = args['link']
        document.flag = args['flag']
        session.commit()
        return jsonify({'success': 'OK',
                        'document': document.to_dict(only=('id', 'name', 'link', 'state', 'flag', 'update_date', 'user.login', 'user.password'))})

    def delete(self, doc_id):
        session = create_session()
        document = session.query(Document).get(doc_id)
        if not document:
            return jsonify({'error': 'записи с таким id не существует'})
        user: User = document.user
        if len(user.documents) <= 1:
            print('delete user', user.login)
            session.delete(user)
        session.delete(document)
        session.commit()
        return jsonify({'success': 'OK'})


user_parser = reqparse.RequestParser()
user_parser.add_argument('login', required=True, location='form')
user_parser.add_argument('password', required=True, location='form')


class UserListResource(Resource):
    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify([user.to_dict(only=('id', 'login', 'password', 'status')) for user in users])

    def post(self):
        args = user_parser.parse_args()
        session = create_session()
        if session.query(User).filter(User.login == args['login']):
            return jsonify({'error': "пользователь с таким логином уже зарегистрирован"})
        user = User(login=args['login'], password=args['password'])
        session.add(user)
        session.commit()
