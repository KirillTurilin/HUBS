from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hubs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    dark_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chats_initiated = db.relationship('Chat', foreign_keys='Chat.user1_id', backref='initiator', lazy='dynamic')
    chats_received = db.relationship('Chat', foreign_keys='Chat.user2_id', backref='receiver', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='chat', lazy='dynamic')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', backref='messages')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chats'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chats'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))
        
        if email_exists:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chats'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('chats'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/chats')
@login_required
def chats():
    initiated_chats = Chat.query.filter_by(user1_id=current_user.id).all()
    received_chats = Chat.query.filter_by(user2_id=current_user.id).all()
    all_chats = initiated_chats + received_chats
    
    # Get the other user for each chat
    chat_users = []
    for chat in all_chats:
        other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
        other_user = User.query.get(other_user_id)
        chat_users.append({'chat': chat, 'user': other_user})
    
    return render_template('chats.html', chat_users=chat_users, active_page='chats')

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    
    # Make sure the current user is part of this chat
    if chat.user1_id != current_user.id and chat.user2_id != current_user.id:
        flash('You do not have permission to access this chat!', 'danger')
        return redirect(url_for('chats'))
    
    other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
    other_user = User.query.get(other_user_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(chat_id=chat.id, sender_id=current_user.id, content=content)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('chat', chat_id=chat.id))
    
    messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', chat=chat, other_user=other_user, messages=messages, active_page='chats')

@app.route('/create_chat', methods=['GET', 'POST'])
@login_required
def create_chat():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('User not found!', 'danger')
            return redirect(url_for('create_chat'))
        
        if user.id == current_user.id:
            flash('You cannot chat with yourself!', 'danger')
            return redirect(url_for('create_chat'))
        
        # Check if chat already exists
        existing_chat = Chat.query.filter(
            ((Chat.user1_id == current_user.id) & (Chat.user2_id == user.id)) |
            ((Chat.user1_id == user.id) & (Chat.user2_id == current_user.id))
        ).first()
        
        if existing_chat:
            return redirect(url_for('chat', chat_id=existing_chat.id))
        
        # Create new chat
        new_chat = Chat(user1_id=current_user.id, user2_id=user.id)
        db.session.add(new_chat)
        db.session.commit()
        
        return redirect(url_for('chat', chat_id=new_chat.id))
    
    return render_template('create_chat.html', active_page='chats')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'toggle_theme':
            current_user.dark_mode = not current_user.dark_mode
            db.session.commit()
            flash('Theme preference updated!', 'success')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html', active_page='profile')

@app.route('/search')
@login_required
def search():
    return render_template('search.html', active_page='search')

@app.route('/api/toggle_theme', methods=['POST'])
@login_required
def toggle_theme():
    current_user.dark_mode = not current_user.dark_mode
    db.session.commit()
    return jsonify({'success': True, 'dark_mode': current_user.dark_mode})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 