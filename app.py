from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Jinja2 Filter ---
@app.template_filter('ampm')
def ampm_filter(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p").lstrip('0')
    except ValueError:
        return time_str

# --- Utilities ---
def load_requests():
    try:
        with open("client_requests.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_requests(data):
    with open("client_requests.json", "w") as f:
        json.dump(data, f, indent=4)

def load_blackouts():
    try:
        with open("blackout_dates.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_blackouts(dates):
    with open("blackout_dates.json", "w") as f:
        json.dump(dates, f, indent=4)

# --- Landing Page ---
@app.route('/')
def home():
    try:
        with open("visit_counter.json", "r") as f:
            counter = json.load(f)
    except FileNotFoundError:
        counter = {"visits": 0}

    counter["visits"] += 1

    with open("visit_counter.json", "w") as f:
        json.dump(counter, f)

    return render_template("home.html", visits=counter["visits"])

# --- Book Appointment ---
@app.route('/book')
def book():
    blackouts = load_blackouts()
    return render_template("index.html", blackouts=blackouts)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    service = request.form['service']
    date = request.form['date']
    time = request.form['time']
    dt = f"{date} {time}"

    new_request = {
        "name": name,
        "phone": phone,
        "email": email,
        "service": service,
        "datetime": dt
    }

    data = load_requests()
    data.append(new_request)
    save_requests(data)

    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template("thank_you.html")

# --- Admin Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "<h3>Incorrect password</h3>"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# --- Admin Dashboard ---
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()
    visits = 0
    try:
        with open("visit_counter.json", "r") as f:
            visits = json.load(f).get("visits", 0)
    except FileNotFoundError:
        pass

    blackouts = load_blackouts()
    return render_template("admin.html", requests=requests, visits=visits, blackouts=blackouts)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_requests()
    if 0 <= index < len(data):
        del data[index]
        save_requests(data)

    return redirect(url_for('admin'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_requests()
    if request.method == 'POST':
        data[index] = {
            "name": request.form['name'],
            "phone": request.form['phone'],
            "email": request.form['email'],
            "service": request.form['service'],
            "datetime": f"{request.form['date']} {request.form['time']}"
        }
        save_requests(data)
        return redirect(url_for('admin'))

    return render_template("edit.html", request=data[index], index=index)

# --- Blackout Dates ---
@app.route('/admin/blackout', methods=['POST'])
def add_blackout():
    if not session.get('admin'):
        return redirect(url_for('login'))

    new_date = request.form['blackout_date']
    dates = load_blackouts()
    if new_date not in dates:
        dates.append(new_date)
        save_blackouts(dates)

    return redirect(url_for('admin'))

@app.route('/admin/remove_blackout/<date>', methods=['POST'])
def remove_blackout(date):
    if not session.get('admin'):
        return redirect(url_for('login'))

    dates = load_blackouts()
    if date in dates:
        dates.remove(date)
        save_blackouts(dates)

    return redirect(url_for('admin'))

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
