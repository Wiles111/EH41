from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Landing Page ---
@app.route('/')
def home():
    return render_template('home.html')  # new file

# --- Client Form ---
@app.route('/book')
def book():
    try:
        with open("blackout_schedule.json", "r") as f:
            blackouts = json.load(f)
    except FileNotFoundError:
        blackouts = {"dates": [], "times": []}
        with open("blackout_schedule.json", "w") as f:
            json.dump(blackouts, f, indent=4)

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
    return "<h2>Thank you for your request! We'll contact you soon.</h2>"

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
    return '''
        <form method="post">
            <input type="password" name="password" placeholder="Enter admin password" required>
            <input type="submit" value="Login">
        </form>
    '''

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

if __name__ == '__main__':
    app.run(debug=True)

