import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
import datetime


class Order(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'order'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    product_ides = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    order_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    should_be_delivered = sqlalchemy.Column(sqlalchemy.DateTime,
                                            default=(datetime.datetime.now() + datetime.timedelta(days=2)))
    comment = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    payment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_ordered = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    take_order_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    who_ordered = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    stage = sqlalchemy.Column(sqlalchemy.Text, nullable=False, default=0)
    is_paid = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    user = orm.relation('User')
