import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

Products_in_baskets = sqlalchemy.Table(
    'products_in_baskets',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('product_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('basket_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('baskets.id')),
)


class Product(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'products'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    discount = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
