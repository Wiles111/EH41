import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Jinja2 Filter for AM/PM Display ---
@app.template_filter('ampm')
def ampm_filter(time_str):
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p").lstrip('0')
    except ValueError:
        return time_str

# --- Helpers ---
def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# --- Landing Page ---
@app.route('/')
def home():
    counter = load_json("visit_counter.json", {"visits": 0})
    counter["visits"] += 1
    save_json("visit_counter.json", counter)
    return render_template("home.html", visits=counter["visits"])

# --- Client Booking Page ---
@app.route('/book')
def book():
    blackouts = load_json("blackout_dates.json", [])

    # Generate 30-minute time slots from 7:00 AM to 10:30 PM
    times = []
    for hour in range(7, 23):
        times.append(("%02d:00" % hour, datetime.strptime(f"{hour}:00", "%H:%M").strftime("%I:%M %p").lstrip("0")))
        times.append(("%02d:30" % hour, datetime.strptime(f"{hour}:30", "%H:%M").strftime("%I:%M %p").lstrip("0")))
    times.append(("22:30", "10:30 PM"))

    return render_template("index.html", blackouts=blackouts, times=times)


@app.route('/submit', methods=['POST'])
def submit():
    form = request.form
    new_request = {
        "name": form['name'],
        "phone": form['phone'],
        "email": form['email'],
        "service": form['service'],
        "datetime": f"{form['date']} {form['time']}"
    }
    requests = load_json("client_requests.json", [])
    requests.append(new_request)
    save_json("client_requests.json", requests)
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template("thank_you.html")

# --- Admin Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
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

    requests = load_json("client_requests.json", [])
    blackouts = load_json("blackout_dates.json", [])
    visits = load_json("visit_counter.json", {}).get("visits", 0)
    return render_template("admin.html", requests=requests, blackouts=blackouts, visits=visits)

# --- Admin Edit/Delete Requests ---
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_json("client_requests.json", [])
    if 0 <= index < len(requests):
        requests.pop(index)
        save_json("client_requests.json", requests)
    return redirect(url_for('admin'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_json("client_requests.json", [])
    if request.method == 'POST':
        form = request.form
        requests[index] = {
            "name": form['name'],
            "phone": form['phone'],
            "email": form['email'],
            "service": form['service'],
            "datetime": f"{form['date']} {form['time']}"
        }
        save_json("client_requests.json", requests)
        return redirect(url_for('admin'))

    return render_template("edit.html", request=requests[index], index=index)

# --- Admin Blackout Dates ---
@app.route('/admin/blackout', methods=['POST'])
def add_blackout():
    if not session.get('admin'):
        return redirect(url_for('login'))

    new_date = request.form['blackout_date']
    blackouts = load_json("blackout_dates.json", [])
    if new_date not in blackouts:
        blackouts.append(new_date)
        save_json("blackout_dates.json", blackouts)
    return redirect(url_for('admin'))

@app.route('/admin/remove_blackout/<date>', methods=['POST'])
def remove_blackout(date):
    if not session.get('admin'):
        return redirect(url_for('login'))

    blackouts = load_json("blackout_dates.json", [])
    if date in blackouts:
        blackouts.remove(date)
        save_json("blackout_dates.json", blackouts)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
