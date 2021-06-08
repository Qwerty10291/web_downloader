import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


document_association = sqlalchemy.Table('documentassociations', SqlAlchemyBase.metadata,
                                sqlalchemy.Column(
                                    'user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
                                sqlalchemy.Column('doc_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('documents.id')))


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String, default='nonauthorized')
    documents = orm.relation(
        'Document', secondary=document_association, back_populates='user')


class Document(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'documents'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    link = sqlalchemy.Column(sqlalchemy.String)
    state = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    flag = sqlalchemy.Column(sqlalchemy.String, default='false')
    update_date = sqlalchemy.Column(sqlalchemy.DateTime(), default=datetime.datetime.now())
    user = orm.relation('User', secondary=document_association, back_populates='documents', uselist=False)
