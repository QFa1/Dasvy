import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Products_img(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'products_img'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"), nullable=False)
    img1 = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    img2 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    img3 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    img4 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    img5 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
