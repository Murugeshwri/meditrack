from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "meditrack_ultra_2026"

# Database Connection
def get_db():
    conn = sqlite3.connect("medi_ultra_final.db")
    conn.row_factory = sqlite3.Row
    return conn

# Database Tables Initialize
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, password TEXT, name TEXT, 
            phone TEXT, age INTEGER, gender TEXT, blood TEXT, condition TEXT
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS family (
            id INTEGER PRIMARY KEY AUTOINCREMENT, main_email TEXT,
            f_name TEXT, f_relation TEXT, age INTEGER, gender TEXT, blood TEXT
        )''')

# --- MAIN ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_logic', methods=['POST'])
def register_logic():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    age = request.form.get('age')
    gender = request.form.get('gender')
    blood = request.form.get('blood')
    pwd = request.form.get('password')
    try:
        with get_db() as db:
            db.execute("INSERT INTO users (email, password, name, phone, age, gender, blood) VALUES (?,?,?,?,?,?,?)",
                       (email, pwd, name, phone, age, gender, blood))
            db.commit()
        return redirect(url_for('login'))
    except:
        return "Email already exists! <a href='/register'>Try again</a>"

@app.route('/login_logic', methods=['POST'])
def login_logic():
    email = request.form.get('email')
    pwd = request.form.get('password')
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
    if user:
        session['user_email'] = email
        return redirect(url_for('dashboard'))
    return "Invalid Login! <a href='/login'>Try Again</a>"

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session: return redirect(url_for('login'))
    email = session['user_email']
    with get_db() as db:
        user_data = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        family_data = db.execute("SELECT * FROM family WHERE main_email=?", (email,)).fetchall()
    return render_template('dashboard.html', user=user_data, family=family_data, is_member=False)

@app.route('/member_dashboard/<int:member_id>')
def member_dashboard(member_id):
    if 'user_email' not in session: return redirect(url_for('login'))
    with get_db() as db:
        member_data = db.execute("SELECT * FROM family WHERE id=?", (member_id,)).fetchone()
    return render_template('dashboard.html', user=member_data, is_member=True)

# --- DASHBOARD 6 FUNCTIONS ---

@app.route('/medicines')
def medicines():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('medicines.html')

@app.route('/appointments')
def appointments():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('appointments.html')

@app.route('/reports')
def reports():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('report.html')

@app.route('/emergency')
def emergency():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('emergency.html')

@app.route('/settings')
def settings():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/bmi')
def bmi():
    if 'user_email' not in session: return redirect(url_for('login'))
    return render_template('bmi.html')

# --- SECURITY & PASSWORD (Pudhusaa add panniyadhu) ---

@app.route('/security')
def security():
    if 'user_email' not in session: return redirect(url_for('login'))
    email = session['user_email']
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    return render_template('security.html', user=user)

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_email' not in session: return redirect(url_for('login'))
    new_pwd = request.form.get('new_password')
    email = session['user_email']
    with get_db() as db:
        db.execute("UPDATE users SET password=? WHERE email=?", (new_pwd, email))
        db.commit()
    return "<h3>Password Updated Successfully! <a href='/settings'>Back to Settings</a></h3>"

# --- PROFILE & MEMBER MANAGEMENT ---

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_email' not in session: return redirect(url_for('login'))
    name = request.form.get('name')
    age = request.form.get('age')
    blood = request.form.get('blood')
    condition = request.form.get('condition')
    email = session['user_email']
    with get_db() as db:
        db.execute("UPDATE users SET name=?, age=?, blood=?, condition=? WHERE email=?", 
                   (name, age, blood, condition, email))
        db.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_member_logic', methods=['POST'])
def add_member_logic():
    if 'user_email' not in session: return redirect(url_for('login'))
    email = session['user_email']
    f_name = request.form.get('f_name')
    f_relation = request.form.get('f_relation')
    f_age = request.form.get('age')
    f_gender = request.form.get('gender')
    f_blood = request.form.get('blood')
    with get_db() as db:
        db.execute("INSERT INTO family (main_email, f_name, f_relation, age, gender, blood) VALUES (?,?,?,?,?,?)", 
                   (email, f_name, f_relation, f_age, f_gender, f_blood))
        db.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_member/<int:member_id>')
def delete_member(member_id):
    if 'user_email' not in session: return redirect(url_for('login'))
    with get_db() as db:
        db.execute("DELETE FROM family WHERE id=?", (member_id,))
        db.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)