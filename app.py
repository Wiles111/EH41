from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
# Register a custom Jinja2 filter to convert 24h time to 12h AM/PM
@app.template_filter('ampm')
def ampm_filter(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p").lstrip('0')
    except ValueError:
        return time_str  # fallback if something goes wrong

app.secret_key = "your-secret-key"  # Needed for session management

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

# --- Client Booking Page ---
@app.route('/book')
def book():
    return render_template("index.html")

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

# --- Admin Login & Dashboard ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == "adminpass":  # Change this securely for production
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            return "<h3>Incorrect password</h3>"
    return render_template("login.html")

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()

    try:
        with open("visit_counter.json", "r") as f:
            counter = json.load(f)
            visits = counter.get("visits", 0)
    except FileNotFoundError:
        visits = 0

    return render_template("admin.html", requests=requests, visits=visits)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# --- Delete Appointment ---
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_requests()
    if 0 <= index < len(data):
        del data[index]
        save_requests(data)

    return redirect(url_for('admin'))

# --- Edit Appointment ---
@app.route('/edit/<int:index>', methods=['GET'])
def edit(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_requests()
    if 0 <= index < len(data):
        return render_template("edit.html", request=data[index], index=index)
    return redirect(url_for('admin'))

@app.route('/update/<int:index>', methods=['POST'])
def update(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    data = load_requests()
    if 0 <= index < len(data):
        data[index] = {
            "name": request.form['name'],
            "phone": request.form['phone'],
            "email": request.form['email'],
            "service": request.form['service'],
            "datetime": f"{request.form['date']} {request.form['time']}"
        }
        save_requests(data)

    return redirect(url_for('admin'))

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
