from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"


# --- Helper to load blackout data ---
def load_blackout_data():
    try:
        with open("blackout.json", "r") as f:
            data = json.load(f)
            return data.get("dates", []), data.get("times", [])
    except FileNotFoundError:
        return [], []


# --- Landing Page ---
@app.route('/')
def home():
    return render_template('home.html')


# --- Client Booking Page ---
@app.route('/book')
def book():
    blackout_dates, blackout_times = load_blackout_data()
    return render_template('index.html', blackouts=blackout_dates, blocked_times=blackout_times)


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

    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(new_request)

    with open("client_requests.json", "w") as f:
        json.dump(data, f, indent=4)

    return redirect(url_for('thank_you'))


@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')


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
    return render_template('login.html')


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

    return render_template('admin.html', requests=requests)


# --- Modify Availability Page ---
@app.route('/availability', methods=['GET', 'POST'])
def modify_availability():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_date = request.form.get('blackout_date')
        new_time = request.form.get('blackout_time')

        try:
            with open("blackout.json", "r") as f:
                blackout_data = json.load(f)
        except FileNotFoundError:
            blackout_data = {"dates": [], "times": []}

        if new_date and new_date not in blackout_data["dates"]:
            blackout_data["dates"].append(new_date)

        if new_time and new_time not in blackout_data["times"]:
            blackout_data["times"].append(new_time)

        with open("blackout.json", "w") as f:
            json.dump(blackout_data, f, indent=4)

        return redirect(url_for('modify_availability'))

    blackout_dates, blackout_times = load_blackout_data()
    return render_template("availability.html", blackout_dates=blackout_dates, blackout_times=blackout_times)


# --- Approve Request (Admin marks a date as unavailable) ---
@app.route('/approve/<int:request_index>', methods=['POST'])
def approve(request_index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
        request_item = data[request_index]
        date_str = request_item["datetime"].split(" ")[0]  # Just the date part
    except (FileNotFoundError, IndexError, KeyError):
        return redirect(url_for('admin'))

    try:
        with open("blackout.json", "r") as f:
            blackout_data = json.load(f)
    except FileNotFoundError:
        blackout_data = {"dates": [], "times": []}

    if date_str not in blackout_data["dates"]:
        blackout_data["dates"].append(date_str)

    with open("blackout.json", "w") as f:
        json.dump(blackout_data, f, indent=4)

    return redirect(url_for('admin'))


# --- Delete Request ---
@app.route('/delete/<int:request_index>', methods=['POST'])
def delete_request(request_index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
        if 0 <= request_index < len(data):
            del data[request_index]
        with open("client_requests.json", "w") as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        pass

    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)




