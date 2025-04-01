import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize SQLite database with categories
def init_db():
    conn = sqlite3.connect('pulse_of_success.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 author TEXT NOT NULL,
                 category TEXT NOT NULL,
                 content TEXT NOT NULL,
                 image_path TEXT,
                 timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Save article to database
def save_article(title, author, category, content, image_path):
    conn = sqlite3.connect('pulse_of_success.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO articles (title, author, category, content, image_path, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (title, author, category, content, image_path, timestamp))
    conn.commit()
    conn.close()

# Load all articles
def load_articles(category=None):
    conn = sqlite3.connect('pulse_of_success.db')
    c = conn.cursor()
    if category:
        c.execute("SELECT id, title, author, category, image_path, timestamp FROM articles WHERE category = ? ORDER BY timestamp DESC", (category,))
    else:
        c.execute("SELECT id, title, author, category, image_path, timestamp FROM articles ORDER BY timestamp DESC")
    articles = [{'id': row[0], 'title': row[1], 'author': row[2], 'category': row[3], 'image_path': row[4], 'timestamp': row[5]} for row in c.fetchall()]
    conn.close()
    return articles

# Load single article
def load_article(article_id):
    conn = sqlite3.connect('pulse_of_success.db')
    c = conn.cursor()
    c.execute("SELECT title, author, category, content, image_path, timestamp FROM articles WHERE id = ?", (article_id,))
    row = c.fetchone()
    conn.close()
    return {'title': row[0], 'author': row[1], 'category': row[2], 'content': row[3], 'image_path': row[4], 'timestamp': row[5]} if row else None

# Homepage
@app.route('/')
def home():
    articles = load_articles()
    categories = ['Business', 'Lifestyle', 'Personal Finance', 'Sports', 'Success']
    return render_template('index.html', articles=articles, categories=categories)

# Category filter
@app.route('/category/<category>')
def category_view(category):
    articles = load_articles(category)
    categories = ['Business', 'Lifestyle', 'Personal Finance', 'Sports', 'Success']
    return render_template('index.html', articles=articles, categories=categories, current_category=category)

# Article detail page
@app.route('/article/<int:article_id>')
def article_detail(article_id):
    article = load_article(article_id)
    if not article:
        return "Article not found", 404
    return render_template('article.html', article=article)

# Contributor submission
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        content = request.form['content']
        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        save_article(title, author, category, content, image_path)
        return redirect(url_for('home'))
    categories = ['Business', 'Lifestyle', 'Personal Finance', 'Sports', 'Success']
    return render_template('submit.html', categories=categories)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(debug=True)