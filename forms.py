# vip_glavbukh_interface/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ConsultantPlusForm(FlaskForm):
    query = TextAreaField('Ваш запрос', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Отправить')

class SettingsForm(FlaskForm):
    username = StringField('Новое имя пользователя', validators=[Optional(), Length(min=4, max=150)])
    password = PasswordField('Новый пароль', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[Optional(), EqualTo('password')])
    submit = SubmitField('Сохранить изменения')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class ConsultationForm(FlaskForm):
    message = TextAreaField('Сообщение', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Введите ваш вопрос...", "rows": 3}
    )
    submit = SubmitField('Отправить')

class CredentialsForm(FlaskForm):
    system_name = StringField(
        'Название системы',
        validators=[DataRequired(message="Пожалуйста, введите название системы.")]
    )
    system_username = StringField(
        'Имя пользователя',
        validators=[DataRequired(message="Пожалуйста, введите имя пользователя.")]
    )
    system_password = StringField(
        'Пароль',
        validators=[DataRequired(message="Пожалуйста, введите пароль.")]
    )
    submit = SubmitField('Сохранить')
