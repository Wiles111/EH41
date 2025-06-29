from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Utility function to load blackout data
def load_blackout_data():
    try:
        with open("blackout.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"dates": [], "times": [], "datetimes": []}
    return data

# --- Home Landing Page ---
@app.route('/')
def home():
    return render_template('home.html')

# --- Client Booking Page ---
@app.route('/book')
def book():
    blackouts = load_blackout_data()
    return render_template('index.html', blackouts=blackouts)

# --- Submit Client Appointment ---
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    service = request.form['service']
    date = request.form['date']
    time = request.form['time']
    dt = f"{date} {time}"

    # --- Load blackout dates/times ---
    blackout_data = load_blackout_data()

    # Check if blocked
    if (
        date in blackout_data.get("dates", []) or
        time in blackout_data.get("times", []) or
        dt in blackout_data.get("datetimes", [])
    ):
        return "<h3 style='color: pink; background-color: black; text-align: center;'>This appointment slot is unavailable. Please <a href='/book'>try again</a>.</h3>"

    new_request = {
        "name": name,
        "phone": phone,
        "email": email,
        "service": service,
        "date": date,
        "time": time,
        "datetime": dt
    }

    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(new_request)

    with open("client_requests.json", "w") as f:
        json.dump(data, f, indent=4)

    return redirect(url_for('thank_you'))

# --- Admin Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
        return "<h3>Incorrect password</h3>"
    return render_template("login.html")

# --- Admin Dashboard ---
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
    except FileNotFoundError:
        requests = []

    blackouts = load_blackout_data()
    return render_template("admin.html", requests=requests, blackouts=blackouts)

# --- Approve Booking and Add to Blackout ---
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)

        approved = data[index]
        blackout = load_blackout_data()

        if approved["date"] not in blackout["dates"]:
            blackout["dates"].append(approved["date"])
        if approved["time"] not in blackout["times"]:
            blackout["times"].append(approved["time"])
        if approved["datetime"] not in blackout["datetimes"]:
            blackout["datetimes"].append(approved["datetime"])

        with open("blackout.json", "w") as f:
            json.dump(blackout, f, indent=4)

        return redirect(url_for('admin'))
    except Exception as e:
        return f"<h3>Error approving: {e}</h3>"

# --- Modify Availability Page ---
@app.route('/availability', methods=['GET', 'POST'])
def modify_availability():
    blackout_data = load_blackout_data()

    if request.method == 'POST':
        date = request.form.get('blackout_date')
        time = request.form.get('blackout_time')

        if date and date not in blackout_data["dates"]:
            blackout_data["dates"].append(date)
        if time and time not in blackout_data["times"]:
            blackout_data["times"].append(time)

        with open('blackout.json', 'w') as f:
            json.dump(blackout_data, f, indent=4)

    return render_template('availability.html', blackouts=blackout_data)

# --- Thank You Page ---
@app.route('/thank-you')
def thank_you():
    return render_template("thank_you.html")

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)


