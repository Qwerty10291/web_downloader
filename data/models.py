import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


document_association = sqlalchemy.Table('documentassociations', SqlAlchemyBase.metadata,
                                sqlalchemy.Column(
                                    'user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
                                sqlalchemy.Column('doc_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('documents.id')))


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    documents = orm.relation(
        'Document', secondary=document_association, backref='documents')


class Document(SqlAlchemyBase):
    __tablename__ = 'documents'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String)
    state = sqlalchemy.Column(sqlalchemy.String)
    flag = sqlalchemy.Column(sqlalchemy.String, default='False')
    user = orm.relation('User', secondary=document_association, backref='user')
