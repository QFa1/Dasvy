from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class FindForm(FlaskForm):
    find = StringField('', validators=[DataRequired()])
    search = SubmitField('Найти')
