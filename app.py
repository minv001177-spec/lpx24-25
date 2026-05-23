from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = 'scootify-secret-key-2025-very-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== СЧЁТЧИК ПОСЕЩЕНИЙ (ЛР 15-16) ==========
@app.before_request
def count_visits():
    # Игнорируем статические файлы
    if request.endpoint and not request.endpoint.startswith('static'):
        if 'visit_count' in session:
            session['visit_count'] = session['visit_count'] + 1
        else:
            session['visit_count'] = 1

# ========== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ==========
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode('utf-8')
    
    def check_password(self, password):
        password_bytes = password.encode('utf-8')
        stored_hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, stored_hash_bytes)
    
    def get_full_info(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio or 'Пользователь пока ничего не рассказал о себе',
            'avatar': self.avatar or '/static/default-avatar.png',
            'created_at': self.created_at.strftime('%d.%m.%Y'),
            'last_login': self.last_login.strftime('%d.%m.%Y %H:%M') if self.last_login else 'Ни разу',
            'is_active': self.is_active
        }
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
    
    def __repr__(self):
        return f'<User {self.username}>'

# ========== ДЕКОРАТОР ДЛЯ ЗАЩИТЫ МАРШРУТОВ ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в аккаунт для доступа к этой странице', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def index():
    return render_template('index.html')

# ========== РЕГИСТРАЦИЯ ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('Пароль должен содержать минимум 4 символа', 'error')
            return render_template('register.html')
        
        if User.get_by_username(username):
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')
        
        if User.get_by_email(email):
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Регистрация прошла успешно! Теперь вы можете войти, {username}', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# ========== ВХОД (ФОРМА ВХОДА ЛР 15-16) ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            user.update_last_login()
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

# ========== ВЫХОД (ЛР 15-16) ==========
@app.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    if username:
        flash(f'До свидания, {username}!', 'info')
    return redirect(url_for('index'))

# ========== ПРОФИЛЬ ==========
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('profile.html', user=user.get_full_info())

# ========== РЕДАКТИРОВАНИЕ ПРОФИЛЯ ==========
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_bio = request.form.get('bio')
        new_password = request.form.get('new_password')
        
        if new_username != user.username:
            existing = User.get_by_username(new_username)
            if existing:
                flash('Пользователь с таким именем уже существует!', 'error')
                return render_template('edit_profile.html', user=user)
        
        if new_email != user.email:
            existing = User.get_by_email(new_email)
            if existing:
                flash('Пользователь с таким email уже существует!', 'error')
                return render_template('edit_profile.html', user=user)
        
        user.username = new_username
        user.email = new_email
        user.bio = new_bio
        
        if new_password and len(new_password) >= 4:
            user.set_password(new_password)
            flash('Пароль обновлён!', 'success')
        
        db.session.commit()
        session['username'] = user.username
        
        flash('Профиль успешно обновлён!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user)

# ========== СЕКРЕТНАЯ СТРАНИЦА ==========
@app.route('/secret')
@login_required
def secret_page():
    user = User.query.get(session['user_id'])
    return render_template('secret.html', username=user.username)

# ========== ВОССТАНОВЛЕНИЕ ПАРОЛЯ ==========
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_by_email(email)
        
        if not user:
            flash('Пользователь с таким email не найден!', 'error')
            return render_template('forgot_password.html')
        
        return render_template('forgot_password.html', reset_mode=True, email=email, user=user)
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('Пароли не совпадают!', 'error')
        return render_template('forgot_password.html', reset_mode=True, email=email)
    
    if len(new_password) < 4:
        flash('Пароль должен быть не менее 4 символов!', 'error')
        return render_template('forgot_password.html', reset_mode=True, email=email)
    
    user = User.get_by_email(email)
    if user:
        user.set_password(new_password)
        db.session.commit()
        flash('Пароль успешно изменён! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    
    flash('Ошибка при сбросе пароля!', 'error')
    return render_template('forgot_password.html')

# ========== ОБРАТНАЯ СВЯЗЬ (ЛР 15-16) ==========
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if message:
            with open('feedback.txt', 'a', encoding='utf-8') as f:
                f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"Имя: {name or session.get('username', 'Аноним')}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Сообщение: {message}\n")
                f.write("-" * 50 + "\n\n")
            
            session['feedback_sent'] = True
            flash('Спасибо за ваш отзыв!', 'success')
            return redirect(url_for('feedback'))
        else:
            flash('Пожалуйста, напишите текст сообщения', 'error')
    
    if request.method == 'GET' and 'feedback_sent' in session:
        session.pop('feedback_sent', None)
    
    return render_template('feedback.html')

# ========== ГОСТЕВАЯ КНИГА (Задание 5 - Вариант А) ==========
@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        name = request.form.get('name')
        comment = request.form.get('comment')
        
        if comment:
            comments = session.get('guestbook_comments', [])
            comments.append({
                'name': name or 'Аноним',
                'text': comment,
                'date': datetime.now().strftime('%d.%m.%Y %H:%M')
            })
            if len(comments) > 20:
                comments = comments[-20:]
            session['guestbook_comments'] = comments
            flash('Ваш комментарий добавлен!', 'success')
        else:
            flash('Пожалуйста, напишите комментарий', 'error')
        
        return redirect(url_for('guestbook'))
    
    return render_template('guestbook.html')

@app.route('/guestbook/clear', methods=['POST'])
def guestbook_clear():
    session.pop('guestbook_comments', None)
    flash('Гостевая книга очищена', 'info')
    return redirect(url_for('guestbook'))

# ========== СОЗДАНИЕ БАЗЫ ДАННЫХ ==========
with app.app_context():
    db.create_all()
    print("✅ База данных готова!")

if __name__ == '__main__':
    app.run(debug=True)