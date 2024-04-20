from flask_wtf import FlaskForm
from flask_login import login_manager, UserMixin, LoginManager
from wtforms import (PasswordField, StringField, SubmitField, BooleanField, IntegerField, TextField, TextAreaField,
                     FileField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterEmail(FlaskForm):
    code = IntegerField('Код', validators=[DataRequired()])
    submit2 = SubmitField('Подтвердить')


class Contacts(FlaskForm):
    full_name = StringField('ФИО', validators=[DataRequired()])
    phone_number = StringField('Контактный телефон', validators=[DataRequired()])
    district = TextField('Район', validators=[DataRequired()])
    street = TextField('Улица', validators=[DataRequired()])
    home = TextField('Дом', validators=[DataRequired()])
    flat = TextField('Квартира')
    comment = TextAreaField('')
    submit = SubmitField('Продолжить')


class RedactProfile(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество')
    email = EmailField('Почта', validators=[DataRequired()])
    phone_number = StringField('Контактный телефон')
    district = TextField('Район')
    street = TextField('Улица')
    home = TextField('Дом')
    flat = TextField('Квартира')
    profile_photo = FileField('Прикрепить фото профиля')
    submit = SubmitField('Изменить')
