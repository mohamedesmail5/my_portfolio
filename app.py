from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS about (id INTEGER PRIMARY KEY, content TEXT)")
    c.execute('SELECT COUNT(*) FROM about')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO about (content) VALUES (?)', ("I'm an AI Engineer...",))

    c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, image TEXT, github TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS contact (id INTEGER PRIMARY KEY, content TEXT)")
    c.execute('SELECT COUNT(*) FROM contact')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO contact (content) VALUES (?)', ("",))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT content FROM about LIMIT 1')
    about = c.fetchone()[0]
    c.execute('SELECT * FROM projects')
    projects = c.fetchall()
    conn.close()
    return render_template('index.html', about=about, projects=projects)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        if 'about' in request.form:
            about = request.form['about']
            c.execute('UPDATE about SET content=? WHERE id=1', (about,))
        elif 'contact_content' in request.form:
            contact_content = request.form['contact_content']
            c.execute('UPDATE contact SET content=? WHERE id=1', (contact_content,))
        conn.commit()

    c.execute('SELECT content FROM about LIMIT 1')
    about = c.fetchone()[0]
    c.execute('SELECT * FROM projects')
    projects = c.fetchall()
    c.execute('SELECT content FROM contact LIMIT 1')
    contact_content = c.fetchone()[0]
    conn.close()
    return render_template('admin.html', about=about, projects=projects, contact_content=contact_content)

@app.route('/add_project', methods=['POST'])
def add_project():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    github = request.form.get('github')
    image = request.files['image']
    image_path = None
    if image:
        image_path = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_path))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO projects (title, description, image, github) VALUES (?, ?, ?, ?)', (title, description, image_path, github))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/delete/<int:project_id>')
def delete_project(project_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id=?', (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'mohamed esmail' and request.form['password'] == '1412005':
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/contact')
def contact():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT content FROM contact LIMIT 1')
    contact_info = c.fetchone()[0]
    conn.close()
    return render_template('contact.html', contact_info=contact_info)

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    file = request.files.get('cv_file')
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join('static', 'files', 'cv.pdf')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
