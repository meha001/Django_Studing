from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
import os
from datetime import datetime
from models import db, User, Post, Comment, Category, Tag, Like
from forms import (RegistrationForm, LoginForm, UpdateProfileForm, PostForm, 
                  CommentForm, CategoryForm)
import bleach
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/avatars')

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_avatar(form_avatar):
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_avatar.filename)
    avatar_fn = random_hex + f_ext
    avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], avatar_fn)
    
    output_size = (150, 150)
    i = Image.open(form_avatar)
    i.thumbnail(output_size)
    i.save(avatar_path)
    
    return avatar_fn

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.is_pinned.desc(), 
                              Post.date_posted.desc()).paginate(page=page, 
                                                              per_page=10)
    categories = Category.query.all()
    return render_template('home.html', posts=posts, categories=categories)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                   email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Ваша учетная запись создана! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Войти не удалось. Проверьте email и пароль', 'danger')
    return render_template('login.html', title='Вход', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = save_avatar(form.avatar.data)
            current_user.avatar = avatar_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Ваш профиль обновлен!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    return render_template('profile.html', title='Профиль', form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                   content=bleach.clean(form.content.data),
                   author=current_user,
                   category_id=form.category.data)
        
        # Обработка тегов
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост создан!', 'success')
        return redirect(url_for('post', slug=post.slug))
    return render_template('create_post.html', title='Новый пост',
                         form=form, legend='Новый пост')

@app.route("/post/<string:slug>", methods=['GET', 'POST'])
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите, чтобы оставить комментарий.', 'info')
            return redirect(url_for('login'))
        comment = Comment(content=bleach.clean(form.content.data),
                        post=post,
                        author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий добавлен!', 'success')
        return redirect(url_for('post', slug=post.slug))
    return render_template('post.html', title=post.title, post=post, form=form)

@app.route("/post/<string:slug>/update", methods=['GET', 'POST'])
@login_required
def update_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = bleach.clean(form.content.data)
        post.category_id = form.category.data
        post.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        db.session.commit()
        flash('Ваш пост обновлен!', 'success')
        return redirect(url_for('post', slug=post.slug))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category_id
        form.tags.data = ', '.join(tag.name for tag in post.tags)
    return render_template('create_post.html', title='Обновить пост',
                         form=form, legend='Обновить пост')

@app.route("/post/<string:slug>/delete", methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Ваш пост удален!', 'success')
    return redirect(url_for('home'))

@app.route("/category/new", methods=['GET', 'POST'])
@login_required
def new_category():
    if not current_user.is_admin:
        abort(403)
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                          description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Новая категория создана!', 'success')
        return redirect(url_for('home'))
    return render_template('create_category.html', title='Новая категория',
                         form=form, legend='Новая категория')

@app.route("/category/<string:slug>")
def category_posts(slug):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    category = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter_by(category=category)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=per_page)
    return render_template('category_posts.html', posts=posts,
                         category=category)

@app.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user=current_user, post=post).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'likes': post.like_count, 'liked': False})
    like = Like(user=current_user, post=post)
    db.session.add(like)
    db.session.commit()
    return jsonify({'likes': post.like_count, 'liked': True})

@app.route("/comment/<int:comment_id>/like", methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    like = Like.query.filter_by(user=current_user, comment=comment).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'likes': comment.like_count, 'liked': False})
    like = Like(user=current_user, comment=comment)
    db.session.add(like)
    db.session.commit()
    return jsonify({'likes': comment.like_count, 'liked': True})

@app.route("/search")
def search():
    query = request.args.get('q')
    if query:
        posts = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) |
            (Post.content.ilike(f'%{query}%'))
        ).order_by(Post.date_posted.desc()).all()
    else:
        posts = []
    return render_template('search.html', posts=posts, query=query)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
        # Создаем категорию по умолчанию, если её нет
        if not Category.query.first():
            default_category = Category(name='Общее', description='Общая категория для обсуждений')
            db.session.add(default_category)
            db.session.commit()
    app.run(debug=True) 