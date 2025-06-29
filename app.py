from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

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
        with open("blackouts.json", "r") as f:
            blackouts = json.load(f)
    except FileNotFoundError:
        blackouts = {"dates": [], "times": []}
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

# --- Approve Booking and Blackout the Date ---
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
        selected = requests[index]
        date_only = selected["datetime"].split()[0]

        try:
            with open("blackouts.json", "r") as f:
                blackouts = json.load(f)
        except FileNotFoundError:
            blackouts = {"dates": [], "times": []}

        if date_only not in blackouts["dates"]:
            blackouts["dates"].append(date_only)

        with open("blackouts.json", "w") as f:
            json.dump(blackouts, f, indent=4)

        return redirect(url_for('admin'))
    except Exception as e:
        return f"Error approving request: {e}"

# --- Delete Booking ---
@app.route('/delete/<int:index>', methods=['POST'])
def delete_request(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
        requests.pop(index)
        with open("client_requests.json", "w") as f:
            json.dump(requests, f, indent=4)
        return redirect(url_for('admin'))
    except Exception as e:
        return f"Error deleting request: {e}"

# --- View & Modify Availability ---
@app.route('/availability')
def modify_availability():
    if not session.get('admin'):
        return redirect(url_for('login'))

    try:
        with open("blackouts.json", "r") as f:
            blackouts = json.load(f)
    except FileNotFoundError:
        blackouts = {"dates": [], "times": []}

    return render_template('availability.html', blackouts=blackouts)

@app.route('/add-blackout', methods=['POST'])
def add_blackout():
    if not session.get('admin'):
        return redirect(url_for('login'))

    date = request.form.get('date')
    time = request.form.get('time')

    try:
        with open("blackouts.json", "r") as f:
            blackouts = json.load(f)
    except FileNotFoundError:
        blackouts = {"dates": [], "times": []}

    if date and date not in blackouts["dates"]:
        blackouts["dates"].append(date)

    if time and time not in blackouts["times"]:
        blackouts["times"].append(time)

    with open("blackouts.json", "w") as f:
        json.dump(blackouts, f, indent=4)

    return redirect(url_for('modify_availability'))

if __name__ == '__main__':
    app.run(debug=True)


