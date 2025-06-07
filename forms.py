from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя',
                         validators=[DataRequired(),
                                   Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль',
                                   validators=[DataRequired(),
                                             EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class UpdateProfileForm(FlaskForm):
    username = StringField('Имя пользователя',
                         validators=[DataRequired(),
                                   Length(min=2, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    bio = TextAreaField('О себе')
    avatar = FileField('Обновить аватар',
                      validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Обновить')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Этот email уже зарегистрирован. Пожалуйста, используйте другой.')

class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    tags = StringField('Теги (разделите запятыми)')
    submit = SubmitField('Опубликовать')

class CommentForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Создать категорию') 