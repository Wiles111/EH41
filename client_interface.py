import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json

# --- Available Services ---
services = ["Eyebrow Tattoo", "Lip Filler", "Eyelash Extensions"]

# --- Save Request to JSON ---
def save_request(name, phone, email, service, dt):
    request = {
        "name": name,
        "phone": phone,
        "email": email,
        "service": service,
        "datetime": dt.strftime("%Y-%m-%d %H:%M")
    }

    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(request)

    with open("client_requests.json", "w") as f:
        json.dump(data, f, indent=4)

# --- Submit Button Logic ---
def submit_request():
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()
    service = selected_service.get()
    date = calendar.get()
    time = f"{hour_var.get()}:{minute_var.get()}"

    if name in ["", "Name"] or phone in ["", "Phone"]:
        messagebox.showerror("Error", "Name and phone are required.")
        return

    try:
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        save_request(name, phone, email, service, dt)
        messagebox.showinfo("Success", "Appointment request submitted!")
        for entry, placeholder in zip([entry_name, entry_phone, entry_email], ["Name", "Phone", "Email"]):
            entry.delete(0, tk.END)
            add_placeholder(entry, placeholder)
    except ValueError:
        messagebox.showerror("Error", "Invalid date or time format.")

# --- Placeholder Function ---
def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg='gray')

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg='gray')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# --- GUI Layout ---
root = tk.Tk()
root.title("Appointment Request")
root.geometry("360x500")

tk.Label(root, text="Request an Appointment", font=("Helvetica", 16)).pack(pady=10)

# Input Fields
entry_name = tk.Entry(root, width=30)
entry_name.pack()
add_placeholder(entry_name, "Name")

entry_phone = tk.Entry(root, width=30)
entry_phone.pack()
add_placeholder(entry_phone, "Phone")

entry_email = tk.Entry(root, width=30)
entry_email.pack()
add_placeholder(entry_email, "Email")

# Service Dropdown
tk.Label(root, text="Select Service").pack(pady=(10, 0))
selected_service = tk.StringVar(value=services[0])
dropdown = tk.OptionMenu(root, selected_service, *services)
dropdown.config(width=25)
dropdown.pack()

# Date Picker
tk.Label(root, text="Choose Date").pack()
calendar = DateEntry(root, width=27, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
calendar.pack()

# Time Picker
tk.Label(root, text="Choose Time").pack()
frame_time = tk.Frame(root)
frame_time.pack(pady=5)

hour_var = tk.StringVar(value="12")
minute_var = tk.StringVar(value="00")

spin_hour = tk.Spinbox(frame_time, from_=0, to=23, width=5, textvariable=hour_var, format="%02.0f")
spin_minute = tk.Spinbox(frame_time, from_=0, to=59, width=5, textvariable=minute_var, format="%02.0f")

spin_hour.pack(side=tk.LEFT)
tk.Label(frame_time, text=":").pack(side=tk.LEFT)
spin_minute.pack(side=tk.LEFT)

# Submit Button
tk.Button(root, text="Submit Request", command=submit_request).pack(pady=10)

root.mainloop()
