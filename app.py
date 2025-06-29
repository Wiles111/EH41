from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Jinja filter to format hours into AM/PM
@app.template_filter('ampm')
def ampm(time_str):
    from datetime import datetime
    dt = datetime.strptime(time_str, "%H:%M")
    return dt.strftime("%-I:%M %p")  # Use %#I for Windows if %-I doesn't work



# --- Landing Page ---
@app.route('/')
def home():
    return render_template('home.html')  # new file

# --- Client Form ---
@app.route('/client')
def client():
    return render_template('index.html')  # was previously at '/'

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
            # re-render the login form with error message
            return render_template('login.html', error="Incorrect password")
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

if __name__ == '__main__':
    app.run(debug=True)

