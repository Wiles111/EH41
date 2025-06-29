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
    try:
        with open("visit_counter.json", "r") as f:
            counter = json.load(f)
    except FileNotFoundError:
        counter = {"visits": 0}

    counter["visits"] += 1

    with open("visit_counter.json", "w") as f:
        json.dump(counter, f)

    return render_template("home.html", visits=counter["visits"])


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
            # re-render the login form with error message
            return render_template('login.html', error="Incorrect password")
    return render_template('login.html')


# --- Admin Dashboard ---
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()

    try:
        with open("visit_counter.json", "r") as f:
            counter = json.load(f)
            visits = counter.get("visits", 0)
    except FileNotFoundError:
        visits = 0

    return render_template('admin.html', requests=requests, visits=visits)


# (app setup code...)

# Load requests from JSON file
def load_requests():
    try:
        with open("client_requests.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save requests to JSON file
def save_requests(requests):
    with open("client_requests.json", "w") as f:
        json.dump(requests, f, indent=4)

# DELETE route
@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()
    if 0 <= index < len(requests):
        del requests[index]
        save_requests(requests)

    return redirect(url_for('admin'))

# EDIT form route
@app.route('/edit/<int:index>', methods=['GET'])
def edit(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()
    if 0 <= index < len(requests):
        return render_template("edit.html", request=requests[index], index=index)
    return redirect(url_for('admin'))

# UPDATE after editing
@app.route('/update/<int:index>', methods=['POST'])
def update(index):
    if not session.get('admin'):
        return redirect(url_for('login'))

    requests = load_requests()
    if 0 <= index < len(requests):
        requests[index] = {
            "name": request.form['name'],
            "phone": request.form['phone'],
            "email": request.form['email'],
            "service": request.form['service'],
            "datetime": f"{request.form['date']} {request.form['time']}"
        }
        save_requests(requests)

    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)

