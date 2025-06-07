from app import app, db
from models import User, Category, Post, Tag
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    with app.app_context():
        # Создаем таблицы
        db.create_all()

        # Создаем администратора
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True,
            bio='Администратор форума'
        )
        db.session.add(admin)

        # Создаем категории
        categories = [
            Category(name='Общее', description='Общие обсуждения'),
            Category(name='Новости', description='Последние новости и обновления'),
            Category(name='Помощь', description='Вопросы и ответы'),
            Category(name='Идеи', description='Предложения по улучшению'),
            Category(name='Технологии', description='Обсуждение технологий')
        ]
        for category in categories:
            db.session.add(category)

        # Создаем теги
        tags = [
            Tag(name='новости'),
            Tag(name='помощь'),
            Tag(name='обсуждение'),
            Tag(name='идеи'),
            Tag(name='технологии')
        ]
        for tag in tags:
            db.session.add(tag)

        # Сохраняем изменения
        db.session.commit()

        # Создаем тестовый пост
        post = Post(
            title='Добро пожаловать на форум!',
            content='Это первый пост на нашем форуме. Здесь вы можете общаться, делиться идеями и помогать друг другу.',
            author=admin,
            category=categories[0],
            is_pinned=True
        )
        post.tags.extend([tags[2], tags[3]])
        db.session.add(post)

        # Сохраняем все изменения
        db.session.commit()

if __name__ == '__main__':
    init_db() 