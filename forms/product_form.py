from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    type = StringField('Тип', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    discount = IntegerField('Цена со скидкой', validators=[(DataRequired())])
    count = IntegerField('Количество', validators=[DataRequired()])
    description = TextAreaField('Описание')
    image1 = FileField('1')
    image2 = FileField('2')
    image3 = FileField('3')
    image4 = FileField('4')
    image5 = FileField('5')
    submit = SubmitField('Добавить')


class CommentsForm(FlaskForm):
    comment = TextAreaField('')
    image = FileField('Прикрепить фото')
    submit = SubmitField('Отправить')
