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
        data = {"dates": [], "times": []}
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
    try:
        with open("blackout.json", "r") as f:
            blackout_data = json.load(f)
    except FileNotFoundError:
        blackout_data = {"dates": [], "times": []}

    if date in blackout_data.get("dates", []) or time in blackout_data.get("times", []):
        return "<h3 style='color: pink; background-color: black; text-align: center;'>This appointment slot is unavailable. Please <a href='/client'>try again</a>.</h3>"

    new_request = {
        "name": name,
        "phone": phone,
        "email": email,
        "service": service,
        "datetime": dt
    }

    # --- Load and save client requests ---
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
    blackout_data = load_blackout_data()
    return render_template("admin.html", requests=requests, blackouts=blackout_data)

# --- Approve Booking and Add to Blackout ---
@app.route('/approve/<int:index>')
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
        approved = data[index]
        blackout = load_blackout_data()
        blackout["dates"].append(approved["date"])
        blackout["times"].append(approved["time"])
        with open("blackout.json", "w") as f:
            json.dump(blackout, f, indent=4)
        return redirect(url_for('admin'))
    except Exception as e:
        return f"Error approving: {e}"

# --- Modify Availability Page ---
@app.route('/availability', methods=['GET', 'POST'])
def modify_availability():
    if not session.get('admin'):
        return redirect(url_for('login'))

    blackout = load_blackout_data()

    if request.method == 'POST':
        new_date = request.form.get("blackout_date")
        new_time = request.form.get("blackout_time")

        if new_date and new_date not in blackout["dates"]:
            blackout["dates"].append(new_date)
        if new_time and new_time not in blackout["times"]:
            blackout["times"].append(new_time)

        with open("blackout.json", "w") as f:
            json.dump(blackout, f, indent=4)

    return render_template("availability.html", blackouts=blackout)

if __name__ == '__main__':
    app.run(debug=True)




