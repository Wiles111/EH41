from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Utilities ---
def load_blackouts():
    try:
        with open("blackout.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"dates": [], "times": []}

def save_blackouts(data):
    with open("blackout.json", "w") as f:
        json.dump(data, f, indent=4)

# --- Landing Page ---
@app.route('/')
def home():
    return render_template("home.html")

# --- Client Booking ---
@app.route('/client')
def client():
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
        if request.form['password'] == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template("login.html", error="Incorrect password")
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

@app.route('/approve/<int:index>')
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)

        approved = data[index]
        date, time = approved['datetime'].split()
        blackouts = load_blackouts()
        if date not in blackouts['dates']:
            blackouts['dates'].append(date)
        if time not in blackouts['times']:
            blackouts['times'].append(time)
        save_blackouts(blackouts)

    except Exception as e:
        print(f"Error approving request: {e}")
    return redirect(url_for('admin'))

@app.route('/delete/<int:index>')
def delete(index):
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)

        data.pop(index)

        with open("client_requests.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error deleting request: {e}")
    return redirect(url_for('admin'))

# --- Modify Availability ---
@app.route('/availability', methods=['GET', 'POST'])
def modify_availability():
    if not session.get('admin'):
        return redirect(url_for('login'))

    blackouts = load_blackouts()

    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')

        if date and date not in blackouts['dates']:
            blackouts['dates'].append(date)
        if time and time not in blackouts['times']:
            blackouts['times'].append(time)

        save_blackouts(blackouts)
        return redirect(url_for('modify_availability'))

    return render_template("availability.html", blackouts=blackouts)

if __name__ == '__main__':
    app.run(debug=True)




