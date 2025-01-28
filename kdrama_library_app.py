from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kdramas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class KDrama(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    poster = db.Column(db.String(300), nullable=True)
    episodes = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String(300), nullable=False)
    main_leads = db.Column(db.String(300), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    release_year = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        kdramas = KDrama.query.all()
        return render_template('library.html', kdramas=kdramas)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
def add_kdrama():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        poster = request.form['poster']
        episodes = request.form['episodes']
        tags = request.form['tags']
        main_leads = request.form['main_leads']
        rating = request.form['rating']
        release_year = request.form['release_year']

        new_kdrama = KDrama(name=name, poster=poster, episodes=episodes, tags=tags,
                            main_leads=main_leads, rating=rating, release_year=release_year)
        db.session.add(new_kdrama)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add.html')

if __name__ == '__main__':
    if not os.path.exists('kdramas.db'):
        db.create_all()
    app.run(debug=True)
