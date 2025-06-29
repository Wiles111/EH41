from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Landing Page ---
@app.route('/')
def home():
    return render_template('home.html')

# --- Client Booking Page ---
@app.route('/client')
def client():
    try:
        with open("blackout_dates.json", "r") as f:
            blackout_dates = json.load(f)
    except FileNotFoundError:
        blackout_dates = []

    try:
        with open("blackout_times.json", "r") as f:
            blackout_times = json.load(f)
    except FileNotFoundError:
        blackout_times = []

    # Create time slots from 7:00 AM to 10:30 PM
    start_time = datetime.strptime("07:00", "%H:%M")
    end_time = datetime.strptime("22:30", "%H:%M")
    time_slots = []
    while start_time <= end_time:
        time_slots.append(start_time.strftime("%-I:%M %p"))  # Ex: 7:30 AM
        start_time += timedelta(minutes=30)

    return render_template("index.html",
                           blackout_dates=blackout_dates,
                           blackout_times=blackout_times,
                           times=time_slots)

# --- Submit Appointment ---
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
        "datetime": dt,
        "approved": False
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

# --- Thank You Page ---
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

    return render_template("admin.html", requests=requests)

# --- Approve Appointment ---
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return redirect(url_for('admin'))

    if 0 <= index < len(data):
        dt = data[index]["datetime"]
        date, time = dt.split(" ", 1)

        # Save blackout date
        try:
            with open("blackout_dates.json", "r") as f:
                blackout_dates = json.load(f)
        except FileNotFoundError:
            blackout_dates = []
        if date not in blackout_dates:
            blackout_dates.append(date)
        with open("blackout_dates.json", "w") as f:
            json.dump(blackout_dates, f, indent=4)

        # Save blackout time
        try:
            with open("blackout_times.json", "r") as f:
                blackout_times = json.load(f)
        except FileNotFoundError:
            blackout_times = []
        if time not in blackout_times:
            blackout_times.append(time)
        with open("blackout_times.json", "w") as f:
            json.dump(blackout_times, f, indent=4)

        data[index]["approved"] = True
        with open("client_requests.json", "w") as f:
            json.dump(data, f, indent=4)

    return redirect(url_for('admin'))

# --- Delete Appointment ---
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    if 0 <= index < len(data):
        del data[index]
        with open("client_requests.json", "w") as f:
            json.dump(data, f, indent=4)

    return redirect(url_for('admin'))

# --- Modify Availability Page ---
@app.route('/modify_availability', methods=['GET', 'POST'])
def modify_availability():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        blackout_date = request.form.get('blackout_date')
        blackout_time = request.form.get('blackout_time')

        if blackout_date:
            try:
                with open("blackout_dates.json", "r") as f:
                    blackout_dates = json.load(f)
            except FileNotFoundError:
                blackout_dates = []

            if blackout_date not in blackout_dates:
                blackout_dates.append(blackout_date)
                with open("blackout_dates.json", "w") as f:
                    json.dump(blackout_dates, f, indent=4)

        if blackout_time:
            try:
                with open("blackout_times.json", "r") as f:
                    blackout_times = json.load(f)
            except FileNotFoundError:
                blackout_times = []

            if blackout_time not in blackout_times:
                blackout_times.append(blackout_time)
                with open("blackout_times.json", "w") as f:
                    json.dump(blackout_times, f, indent=4)

        return redirect(url_for('modify_availability'))

    try:
        with open("blackout_dates.json", "r") as f:
            blackout_dates = json.load(f)
    except FileNotFoundError:
        blackout_dates = []

    try:
        with open("blackout_times.json", "r") as f:
            blackout_times = json.load(f)
    except FileNotFoundError:
        blackout_times = []

    return render_template("availability.html", dates=blackout_dates, times=blackout_times)

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)



