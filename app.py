from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

app = Flask(__name__)
app.app_context().push()
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)  # SQLAlchemy'yi Flask uygulamasına bağlayın

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.Integer, nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def can_access_file():
    return current_user.user_type == 1

def can_write_post():
    return current_user.user_type == 1

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Giriş yapıldı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/file')
@login_required
def file():
    if can_access_file():
        return render_template('file.html', user=current_user)
    else:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı!', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = int(request.form['user_type'])

        with app.app_context():
            new_user = User(username=username, password=password, user_type=user_type)
            db.session.add(new_user)
            db.session.commit()

        flash('Kullanıcı kaydı oluşturuldu, giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/write_post', methods=['GET', 'POST'])
@login_required
def write_post():
    if can_write_post():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            with app.app_context():
                new_post = Post(title=title, content=content, user=current_user)
                db.session.add(new_post)
                db.session.commit()
            flash('Yazı eklendi!', 'success')
            return redirect(url_for('index'))
        return render_template('write_post.html', user=current_user)
    else:
        flash('Bu sayfayı görüntüleme yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
