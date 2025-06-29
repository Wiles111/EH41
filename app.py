

from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Utility: Load blackout data ---
def load_blackout_data():
    try:
        with open("blackout.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"datetimes": []}

# --- Save blackout data ---
def save_blackout_data(data):
    with open("blackout.json", "w") as f:
        json.dump(data, f, indent=4)

# --- Home Page ---
@app.route('/')
def home():
    return render_template("home.html")

# --- Client Booking Page ---
@app.route('/book')
def book():
    blackout_data = load_blackout_data()
    return render_template("index.html", blackouts=blackout_data["datetimes"])

# --- Handle Booking Submission ---
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    service = request.form['service']
    date = request.form['date']
    time = request.form['time']
    dt = f"{date} {time}"

    blackout_data = load_blackout_data()
    if dt in blackout_data.get("datetimes", []):
        return "<h3 style='color: pink; background-color: black; text-align: center;'>This appointment slot is unavailable. Please <a href='/book'>try again</a>.</h3>"

    # Save to client_requests.json
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
    except FileNotFoundError:
        requests = []

    requests.append({
        "name": name,
        "phone": phone,
        "email": email,
        "service": service,
        "date": date,
        "time": time,
        "datetime": dt
    })

    with open("client_requests.json", "w") as f:
        json.dump(requests, f, indent=4)

    return redirect(url_for('thank_you'))

# --- Thank You Page ---
@app.route('/thank-you')
def thank_you():
    return render_template("thank_you.html")

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

    blackout_data = load_blackout_data()
    return render_template("admin.html", requests=requests, blackouts=blackout_data["datetimes"])

# --- Approve Appointment & Add to Blackouts ---
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)

        approved = requests[index]
        dt = approved["datetime"]

        blackout_data = load_blackout_data()
        if dt not in blackout_data["datetimes"]:
            blackout_data["datetimes"].append(dt)
            save_blackout_data(blackout_data)

        return redirect(url_for('admin'))
    except Exception as e:
        return f"Error approving request: {e}"

# --- Delete Appointment ---
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)

        requests.pop(index)

        with open("client_requests.json", "w") as f:
            json.dump(requests, f, indent=4)

        return redirect(url_for('admin'))
    except Exception as e:
        return f"Error deleting request: {e}"

# --- Availability Management Page (Optional Manual Blocking) ---
@app.route('/availability', methods=['GET', 'POST'])
def modify_availability():
    blackout_data = load_blackout_data()

    if request.method == 'POST':
        date = request.form.get("blackout_date")
        time = request.form.get("blackout_time")
        if date and time:
            dt = f"{date} {time}"
            if dt not in blackout_data["datetimes"]:
                blackout_data["datetimes"].append(dt)
                save_blackout_data(blackout_data)

    return render_template("availability.html", blackouts=blackout_data["datetimes"])

if __name__ == "__main__":
    app.run(debug=True)

