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
    
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
        request_to_approve = requests[index]

        # Extract date portion only
        appointment_date = request_to_approve["datetime"].split()[0]

        # Load or initialize blackout file
        try:
            with open("blackouts.json", "r") as f:
                blackouts = json.load(f)
        except FileNotFoundError:
            blackouts = {"dates": [], "times": []}

        # Add to blackout dates if not already present
        if appointment_date not in blackouts["dates"]:
            blackouts["dates"].append(appointment_date)

        # Save updated blackout file
        with open("blackouts.json", "w") as f:
            json.dump(blackouts, f, indent=4)

        return redirect(url_for('admin'))

    except Exception as e:
        return f"Error approving request: {str(e)}"




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
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if password == "adminpass":
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "Incorrect password"
    return render_template('login.html', error=error)


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

from flask import flash  # Optional: for future feedback messages

# Route to approve a request (adds date to blackout list)
@app.route('/approve/<int:index>', methods=['POST'])
def approve(index):
    try:
        with open("client_requests.json", "r") as f:
            requests = json.load(f)
        selected = requests[index]
        date_only = selected["datetime"].split()[0]

        # Load or create blackout file
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

# Route to delete a request
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

# Route to modify availability
@app.route('/availability')
def availability():
    try:
        with open("blackouts.json", "r") as f:
            blackouts = json.load(f)
    except FileNotFoundError:
        blackouts = {"dates": [], "times": []}
    return render_template("availability.html", blackouts=blackouts)


if __name__ == '__main__':
    app.run(debug=True)

